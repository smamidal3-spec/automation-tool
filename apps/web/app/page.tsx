"use client";

import { useEffect, useMemo, useState } from "react";

type RepoType = "devops" | "application";
type ActionType = "replace" | "add";

type PreviewDiff = {
  application: string;
  environment_file: string;
  repo: string;
  changed: boolean;
  diff: string;
  updated_yaml?: string | null;
  error?: string | null;
};

type ExecuteResult = {
  application: string;
  repo: string;
  branch?: string | null;
  pull_request_url?: string | null;
  status: "success" | "failed";
  error?: string | null;
};

type ConfigResponse = {
  approved_keys: string[];
  applications: string[];
  environment_files: string[];
};

const DEFAULT_APPROVED_KEYS = [
  "replicaCount",
  "autoscaling.minReplicas",
  "autoscaling.maxReplicas",
  "image.tag",
  "ingress.annotations.nginx.ingress.kubernetes.io/rewrite-target",
];

const ENV_TO_FILE: Record<string, string> = {
  dev: "values.dev.yaml",
  "qa.east1": "values.qa.east1.yaml",
  "qa.west1": "values.qa.west1.yaml",
  stage: "values.stage.yaml",
  prod: "values.prod.yaml",
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

function parseValue(value: string): unknown {
  const trimmed = value.trim();
  if (trimmed.length === 0) {
    return "";
  }

  try {
    return JSON.parse(trimmed);
  } catch {
    if (trimmed === "true") {
      return true;
    }
    if (trimmed === "false") {
      return false;
    }
    const asNumber = Number(trimmed);
    if (!Number.isNaN(asNumber) && trimmed === String(asNumber)) {
      return asNumber;
    }
    return value;
  }
}

export default function Page() {
  const [appOptions, setAppOptions] = useState<string[]>([]);
  const [approvedKeys, setApprovedKeys] = useState<string[]>(DEFAULT_APPROVED_KEYS);
  const [environmentFiles, setEnvironmentFiles] = useState<string[]>(Object.values(ENV_TO_FILE));

  const [selectedApps, setSelectedApps] = useState<string[]>([]);
  const [repoType, setRepoType] = useState<RepoType>("devops");
  const [actionType, setActionType] = useState<ActionType>("replace");
  const [dryRun, setDryRun] = useState(true);

  const [keyPath, setKeyPath] = useState("image.tag");
  const [newLine, setNewLine] = useState("1.0.1");
  const [filePath, setFilePath] = useState("values.dev.yaml");
  const [environment, setEnvironment] = useState("dev");

  const [previewDiffs, setPreviewDiffs] = useState<PreviewDiff[]>([]);
  const [executeResults, setExecuteResults] = useState<ExecuteResult[]>([]);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [loading, setLoading] = useState<"config" | "preview" | "execute" | "">("config");

  const appCountText = useMemo(
    () => `${selectedApps.length} of ${appOptions.length} selected`,
    [selectedApps.length, appOptions.length],
  );

  useEffect(() => {
    async function loadConfig(): Promise<void> {
      try {
        const response = await fetch(`${API_BASE}/api/v1/automation/config`);
        if (!response.ok) {
          throw new Error(`Config load failed (${response.status})`);
        }

        const data = (await response.json()) as ConfigResponse;
        setAppOptions(data.applications);
        setSelectedApps(data.applications);

        if (data.approved_keys.length > 0) {
          setApprovedKeys(data.approved_keys);
          setKeyPath(data.approved_keys.includes("image.tag") ? "image.tag" : data.approved_keys[0]);
        }
        if (data.environment_files.length > 0) {
          setEnvironmentFiles(data.environment_files);
          setFilePath(data.environment_files[0]);
        }
      } catch {
        setErrorMessage("Could not load repository list. Configure MANAGED_REPOS or GITHUB_ORGS in backend.");
      } finally {
        setLoading("");
      }
    }

    loadConfig();
  }, []);

  function buildHeaders(includeJsonContentType = true): HeadersInit {
    const headers: Record<string, string> = {};
    if (includeJsonContentType) {
      headers["Content-Type"] = "application/json";
    }
    return headers;
  }

  function toggleApp(appName: string): void {
    setSelectedApps((current) => {
      if (current.includes(appName)) {
        return current.filter((item) => item !== appName);
      }
      return [...current, appName];
    });
  }

  function buildEnvironmentFile(): string {
    const trimmedPath = filePath.trim();
    if (trimmedPath.length > 0) {
      return trimmedPath;
    }
    return ENV_TO_FILE[environment] ?? "values.dev.yaml";
  }

  async function runPreview(): Promise<void> {
    setErrorMessage("");
    setExecuteResults([]);

    if (selectedApps.length === 0) {
      setErrorMessage("Select at least one application.");
      return;
    }

    setLoading("preview");
    try {
      const payload = {
        key_path: keyPath,
        new_value: parseValue(newLine),
        targets: selectedApps.map((application) => ({
          application,
          environment_file: buildEnvironmentFile(),
        })),
      };

      const response = await fetch(`${API_BASE}/api/v1/automation/preview`, {
        method: "POST",
        headers: buildHeaders(true),
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const details = await response.text();
        throw new Error(`Preview failed (${response.status}): ${details}`);
      }

      const data = (await response.json()) as { allowed: boolean; diffs: PreviewDiff[] };
      if (!data.allowed) {
        throw new Error("Selected key path is not approved by policy.");
      }

      setPreviewDiffs(data.diffs);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Preview failed.");
    } finally {
      setLoading("");
    }
  }

  async function runExecute(): Promise<void> {
    setErrorMessage("");

    if (previewDiffs.length === 0) {
      setErrorMessage("Run preview first before execute.");
      return;
    }

    setLoading("execute");
    try {
      const payload = {
        key_path: keyPath,
        new_value: parseValue(newLine),
        targets: selectedApps.map((application) => ({
          application,
          environment_file: buildEnvironmentFile(),
        })),
        confirm: true,
        dry_run: dryRun,
      };

      const response = await fetch(`${API_BASE}/api/v1/automation/execute`, {
        method: "POST",
        headers: buildHeaders(true),
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const details = await response.text();
        throw new Error(`Execution failed (${response.status}): ${details}`);
      }

      const data = (await response.json()) as { results: ExecuteResult[] };
      setExecuteResults(data.results);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Execution failed.");
    } finally {
      setLoading("");
    }
  }

  return (
    <main className="page-shell">
      <section className="panel">
        <div className="panel-head">
          <div className="step-pill">1</div>
          <h1 className="title">Applications ({appCountText})</h1>
          <button type="button" className="danger-btn" onClick={() => setSelectedApps([])}>
            Remove Selected
          </button>
        </div>

        <div className="card">
          <label className="field-label">Application Selection</label>
          <div className="app-grid">
            {appOptions.map((appName) => (
              <label key={appName} className="checkbox-option">
                <input type="checkbox" checked={selectedApps.includes(appName)} onChange={() => toggleApp(appName)} />
                <span>{appName}</span>
              </label>
            ))}
          </div>

          {appOptions.length === 0 ? (
            <p className="error-text">No repositories discovered. Set backend `MANAGED_REPOS` or `GITHUB_ORGS`.</p>
          ) : null}

          <label className="field-label">Change in Repository *</label>
          <div className="option-row">
            <label className="radio-option">
              <input type="radio" name="repoType" checked={repoType === "devops"} onChange={() => setRepoType("devops")} />
              <span>DevOps Repo</span>
            </label>
            <label className="radio-option">
              <input
                type="radio"
                name="repoType"
                checked={repoType === "application"}
                onChange={() => setRepoType("application")}
              />
              <span>Application Repo</span>
            </label>
          </div>

          <label className="field-label">Action Type *</label>
          <div className="option-row">
            <label className="radio-option">
              <input
                type="radio"
                name="actionType"
                checked={actionType === "replace"}
                onChange={() => setActionType("replace")}
              />
              <span>Replace Existing Line</span>
            </label>
            <label className="radio-option">
              <input type="radio" name="actionType" checked={actionType === "add"} onChange={() => setActionType("add")} />
              <span>Add New Line</span>
            </label>
          </div>

          <div className="grid-2">
            <div>
              <label className="field-label" htmlFor="keyPath">
                Approved Key Path *
              </label>
              <select id="keyPath" className="text-input" value={keyPath} onChange={(event) => setKeyPath(event.target.value)}>
                {approvedKeys.map((key) => (
                  <option key={key} value={key}>
                    {key}
                  </option>
                ))}
              </select>
            </div>
            <div className="dry-run-wrap">
              <label className="field-label" htmlFor="dryRunToggle">
                Execution Mode
              </label>
              <label className="checkbox-option">
                <input
                  id="dryRunToggle"
                  type="checkbox"
                  checked={dryRun}
                  onChange={(event) => setDryRun(event.target.checked)}
                />
                <span>{dryRun ? "Dry run (no real Git changes)" : "Live mode (real branch/commit/PR)"}</span>
              </label>
            </div>
          </div>

          <label className="field-label" htmlFor="newLine">
            {actionType === "replace" ? "Enter the New Value *" : "Enter the New Line to Add *"}
          </label>
          <textarea
            id="newLine"
            className="text-input text-area"
            value={newLine}
            onChange={(event) => setNewLine(event.target.value)}
            placeholder={"Example: 3 or \"2.1.0\" or true"}
            rows={4}
          />

          <div className="grid-2">
            <div>
              <label className="field-label" htmlFor="filePath">
                File Name and Path *
              </label>
              <input id="filePath" className="text-input" value={filePath} onChange={(event) => setFilePath(event.target.value)} />
            </div>
            <div>
              <label className="field-label" htmlFor="environment">
                Environment
              </label>
              <select
                id="environment"
                className="text-input"
                value={environment}
                onChange={(event) => {
                  const nextEnvironment = event.target.value;
                  setEnvironment(nextEnvironment);
                  setFilePath(ENV_TO_FILE[nextEnvironment] ?? "values.dev.yaml");
                }}
              >
                {Object.keys(ENV_TO_FILE).map((env) => (
                  <option key={env} value={env}>
                    {env}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="field-label">Allowed Environment Files</div>
          <div className="file-chip-row">
            {environmentFiles.map((name) => (
              <span key={name} className="file-chip">
                {name}
              </span>
            ))}
          </div>

          <div className="action-bar">
            <button type="button" className="primary-btn" onClick={runPreview} disabled={loading !== ""}>
              {loading === "preview" ? "Generating Preview..." : "Preview Changes"}
            </button>
            <button
              type="button"
              className="success-btn"
              onClick={runExecute}
              disabled={loading !== "" || previewDiffs.length === 0}
            >
              {loading === "execute" ? "Executing..." : "Execute and Create PR"}
            </button>
          </div>

          {errorMessage ? <p className="error-text">{errorMessage}</p> : null}
          {loading === "config" ? <p>Loading repositories...</p> : null}
        </div>

        {previewDiffs.length > 0 ? (
          <div className="result-panel">
            <h2 className="result-title">Diff Preview</h2>
            {previewDiffs.map((item) => (
              <div key={`${item.application}-${item.environment_file}`} className="result-card">
                <div className="result-meta">
                  <strong>{item.application}</strong>
                  <span>{item.repo}</span>
                  <span>{item.environment_file}</span>
                  <span>{item.changed ? "Changed" : "No change"}</span>
                </div>
                {item.error ? <p className="error-text">{item.error}</p> : <pre className="code-block">{item.diff || "No textual diff"}</pre>}
              </div>
            ))}
          </div>
        ) : null}

        {executeResults.length > 0 ? (
          <div className="result-panel">
            <h2 className="result-title">Execution Summary</h2>
            {executeResults.map((item) => (
              <div key={`${item.application}-${item.repo}`} className="result-card">
                <div className="result-meta">
                  <strong>{item.application}</strong>
                  <span>{item.repo}</span>
                  <span>{item.status}</span>
                  <span>{item.branch ?? "-"}</span>
                </div>
                {item.pull_request_url ? (
                  <a href={item.pull_request_url} target="_blank" rel="noreferrer" className="pr-link">
                    {item.pull_request_url}
                  </a>
                ) : null}
                {item.error ? <p className="error-text">{item.error}</p> : null}
              </div>
            ))}
          </div>
        ) : null}
      </section>
    </main>
  );
}

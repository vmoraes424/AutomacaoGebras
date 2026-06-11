import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { AutomacaoConfig } from "../api/types";
import { GebrasLoader } from "../components/GebrasLoader";
import {
  getStoredConfigPassword,
  setStoredConfigPassword,
} from "../utils/configAuth";

type FlagKey =
  | "dev_pular_clicksign"
  | "teste_plune_sem_assinatura"
  | "dev_hub_sem_aprovacao_plune"
  | "pular_hub"
  | "formulario_web_enabled";

type FlagField = {
  key: FlagKey;
  label: string;
  hint: string;
  productionDefault: boolean;
};

const FLAGS: FlagField[] = [
  {
    key: "dev_pular_clicksign",
    label: "Pular Clicksign (dev)",
    hint: "Não chama a API Clicksign — só gera o .docx localmente.",
    productionDefault: false,
  },
  {
    key: "teste_plune_sem_assinatura",
    label: "Plune sem assinatura (teste)",
    hint: "Cria pedido no Plune logo após o contrato, sem esperar assinatura.",
    productionDefault: false,
  },
  {
    key: "dev_hub_sem_aprovacao_plune",
    label: "HUB sem aprovação Plune (dev)",
    hint: "Cria pedido HUB após Plune no ganho, sem aprovação pós-assinatura.",
    productionDefault: false,
  },
  {
    key: "pular_hub",
    label: "Pular criação no HUB",
    hint: "Desliga criação de pedidos no SOLE HUB (validações continuam).",
    productionDefault: false,
  },
  {
    key: "formulario_web_enabled",
    label: "Formulário web habilitado",
    hint: "Worker usa deal_forms validados; desligado = fluxo legado Pipe-only.",
    productionDefault: true,
  },
];

type FlagPayload = Pick<AutomacaoConfig, FlagKey>;

const PROD_PRESET: FlagPayload = {
  dev_pular_clicksign: false,
  teste_plune_sem_assinatura: false,
  dev_hub_sem_aprovacao_plune: false,
  pular_hub: false,
  formulario_web_enabled: true,
};

const EMPTY: AutomacaoConfig = { ...PROD_PRESET };

export function AutomacaoConfigPage() {
  const [config, setConfig] = useState<AutomacaoConfig>(EMPTY);
  const [passwordRequired, setPasswordRequired] = useState(false);
  const [unlocked, setUnlocked] = useState(false);
  const [passwordInput, setPasswordInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadConfig = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.getAutomacaoConfig();
      setConfig(data);
      setUnlocked(true);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Falha ao carregar";
      if (msg.toLowerCase().includes("senha")) {
        setUnlocked(false);
        setStoredConfigPassword("");
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    api
      .getAutomacaoConfigAccess()
      .then(async (access) => {
        if (!active) return;
        setPasswordRequired(access.password_required);
        if (!access.password_required) {
          await loadConfig();
          return;
        }
        if (getStoredConfigPassword()) {
          await loadConfig();
          return;
        }
        setLoading(false);
      })
      .catch((e: unknown) => {
        if (active) setError(e instanceof Error ? e.message : "Falha ao carregar");
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [loadConfig]);

  const unlock = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setStoredConfigPassword(passwordInput.trim());
    try {
      await loadConfig();
      setPasswordInput("");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Senha inválida");
    } finally {
      setSaving(false);
    }
  };

  const toggle = useCallback((key: FlagKey) => {
    setConfig((prev) => ({ ...prev, [key]: !prev[key] }));
    setMessage("");
    setError("");
  }, []);

  const afterSave = (saved: AutomacaoConfig, label: string) => {
    setConfig(saved);
    setMessage(
      `${label} — salvo em MySQL (${saved.mysql_database ?? "gebras_automacao"}.automacao_config).`,
    );
  };

  const savePayload = async (body: FlagPayload, label = "Configurações") => {
    setSaving(true);
    setMessage("");
    setError("");
    try {
      afterSave(await api.saveAutomacaoConfig(body), label);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Falha ao salvar");
    } finally {
      setSaving(false);
    }
  };

  const applyPreset = async (mode: "dev" | "prod") => {
    setSaving(true);
    setMessage("");
    setError("");
    try {
      const saved =
        mode === "dev"
          ? await api.applyAutomacaoDevPreset()
          : await api.applyAutomacaoProdPreset();
      setConfig(saved);
      afterSave(saved, mode === "dev" ? "Modo Dev aplicado" : "Modo Prod aplicado");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Falha ao aplicar preset");
    } finally {
      setSaving(false);
    }
  };

  const save = () =>
    savePayload({
      dev_pular_clicksign: config.dev_pular_clicksign,
      teste_plune_sem_assinatura: config.teste_plune_sem_assinatura,
      dev_hub_sem_aprovacao_plune: config.dev_hub_sem_aprovacao_plune,
      pular_hub: config.pular_hub,
      formulario_web_enabled: config.formulario_web_enabled,
    });

  const showGate = passwordRequired && !unlocked;

  return (
    <div className="config-page">
      <nav className="page-breadcrumb">
        <Link to="/">← Voltar ao início</Link>
      </nav>

      <header className="config-page-header">
        <div>
          <h2 className="config-page-title">Configs da Automação</h2>
          <p className="config-page-sub muted">
            Flags persistidas na tabela <code>automacao_config</code> do MySQL (
            {config.mysql_database ?? "gebras_automacao"}) — portal e worker leem daqui.
          </p>
          {config.updated_at && unlocked && (
            <p className="config-page-meta muted">Última alteração: {config.updated_at}</p>
          )}
        </div>
      </header>

      {loading && <GebrasLoader variant="inline" label="Carregando…" />}

      {showGate && !loading && (
        <form className="config-card config-gate" onSubmit={(e) => void unlock(e)}>
          <p className="config-gate-text muted">
            Esta tela é protegida. Informe a senha definida em{" "}
            <code>PORTAL_CONFIG_PASSWORD</code> no servidor.
          </p>
          <label className="config-gate-field">
            <span className="config-gate-label">Senha</span>
            <input
              type="password"
              autoComplete="current-password"
              value={passwordInput}
              onChange={(e) => setPasswordInput(e.target.value)}
              disabled={saving}
            />
          </label>
          {error && <div className="alert error">{error}</div>}
          <button type="submit" disabled={saving || !passwordInput.trim()}>
            {saving ? "Verificando…" : "Entrar"}
          </button>
        </form>
      )}

      {!loading && unlocked && (
        <form
          className="config-card"
          onSubmit={(e) => {
            e.preventDefault();
            void save();
          }}
        >
          <ul className="config-flag-list">
            {FLAGS.map((flag) => (
              <li key={flag.key} className="config-flag-item">
                <label className="config-flag-label">
                  <input
                    type="checkbox"
                    checked={Boolean(config[flag.key])}
                    onChange={() => toggle(flag.key)}
                  />
                  <span className="config-flag-text">
                    <span className="config-flag-name">{flag.label}</span>
                    <span className="config-flag-hint">{flag.hint}</span>
                    <span className="config-flag-default muted">
                      Produção recomendada: {flag.productionDefault ? "ligado" : "desligado"}
                    </span>
                  </span>
                </label>
              </li>
            ))}
          </ul>

          {error && <div className="alert error">{error}</div>}
          {message && <div className="alert success">{message}</div>}

          <div className="config-actions">
            <button
              type="button"
              className="secondary"
              disabled={saving}
              onClick={() => void applyPreset("dev")}
            >
              Modo Dev
            </button>
            <button
              type="button"
              className="secondary"
              disabled={saving}
              onClick={() => void applyPreset("prod")}
            >
              Modo Prod
            </button>
            <button type="submit" disabled={saving}>
              {saving ? "Salvando…" : "Salvar configurações"}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

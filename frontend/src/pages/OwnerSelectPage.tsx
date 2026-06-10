import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { CrmUser } from "../api/types";

export function OwnerSelectPage() {
  const [users, setUsers] = useState<CrmUser[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listUsers()
      .then(setUsers)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="layout">
      <h1>Portal Gebras — Selecione o consultor</h1>
      <p className="muted">Escolha o dono dos cards para listar negócios na etapa Contrato.</p>

      {loading && <p>Carregando usuários…</p>}
      {error && <div className="alert error">{error}</div>}

      {!loading &&
        users.map((user) => (
          <div key={user.id} className="card">
            <strong>{user.name}</strong>
            {user.email && <div className="muted">{user.email}</div>}
            <Link className="button" to={`/deals/${user.id}`} state={{ ownerName: user.name }}>
              Ver meus cards
            </Link>
          </div>
        ))}
    </div>
  );
}

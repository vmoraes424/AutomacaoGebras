"""Lista filiais, branches e subcentros gravados no MySQL."""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.database import (
    branch_config,
    db_conn,
    default_branch_id,
    filial_branch_map,
    maps_por_branch,
)


def main() -> int:
    print(f"default_branch_id: {default_branch_id()}\n")
    print("pipedrive_filial (Pipe -> Branch):")
    for k, v in filial_branch_map().items():
        print(f"  {k!r} -> {v}")

    print("\nbranch_config:")
    with db_conn() as conn:
        for row in conn.execute(
            "SELECT branch_id, label, subcentro_custo_id FROM branch_config ORDER BY branch_id"
        ):
            print(
                f"  {row['branch_id']} {row['label']}: subcentro1={row['subcentro_custo_id']}"
            )

    for branch_id in ("751", "790"):
        cfg = branch_config(branch_id)
        maps = maps_por_branch(branch_id)
        if not cfg:
            continue
        print(f"\nBranch {branch_id} — nivel2: {len(maps['regional_map'])}, nivel3: {len(maps['subcentro3_map'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

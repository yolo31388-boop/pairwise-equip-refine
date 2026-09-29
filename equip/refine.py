"""装备精炼与转移系统"""
from dataclasses import dataclass

MAX_REFINE_LEVEL = 20
PITY_THRESHOLD = 10
DESTROY_LEVEL = 10
DESTROY_CHANCE = 0.3


@dataclass
class Equipment:
    eid: str
    name: str
    refine_level: int = 0
    slot: str = "weapon"
    broken: bool = False


class RefineSystem:
    def __init__(self, seed=42):
        import random
        self.rng = random.Random(seed)
        self.equipment: dict[str, Equipment] = {}
        self.fail_count: dict[str, int] = {}
        self.protection_charms: dict[str, int] = {}
        self.failure_penalty_enabled = True

    def get_success_rate(self, level: int) -> float:
        """成功率随精炼等级递减，+10以上成功率极低。"""
        if level >= MAX_REFINE_LEVEL:
            return 0.0
        if level < 10:
            return 0.9 - 0.05 * level
        return max(0.01, 0.45 * (0.6 ** (level - 9)))

    def can_downgrade(self, equip: Equipment) -> bool:
        return self.failure_penalty_enabled and equip.refine_level > 0

    def add_protection_charm(self, eid: str, count: int = 1) -> None:
        self.protection_charms[eid] = self.protection_charms.get(eid, 0) + count

    def _consume_charm(self, eid: str) -> bool:
        if self.protection_charms.get(eid, 0) > 0:
            self.protection_charms[eid] -= 1
            return True
        return False

    def refine(self, eid: str) -> tuple[bool, str]:
        equip = self.equipment[eid]
        if equip.broken:
            return False, "broken"
        if equip.refine_level >= MAX_REFINE_LEVEL:
            return False, "max_level"

        if self.fail_count.get(eid, 0) >= PITY_THRESHOLD:
            equip.refine_level += 1
            self.fail_count[eid] = 0
            return True, "pity_success"

        if self.rng.random() < self.get_success_rate(equip.refine_level):
            equip.refine_level += 1
            self.fail_count[eid] = 0
            return True, "success"

        self.fail_count[eid] = self.fail_count.get(eid, 0) + 1

        if self._consume_charm(eid):
            return False, "protected"

        if equip.refine_level >= DESTROY_LEVEL and self.rng.random() < DESTROY_CHANCE:
            equip.broken = True
            equip.refine_level = 0
            return False, "destroyed"

        if self.can_downgrade(equip):
            equip.refine_level -= 1
            return False, "downgraded"

        return False, "failed"

    def transfer_refine(self, src: str, dst: str) -> int:
        """按比例转移精炼等级，来源等级越高损耗越大。"""
        src_equip = self.equipment[src]
        dst_equip = self.equipment[dst]
        src_level = src_equip.refine_level
        retention = max(0.5, 1.0 - 0.03 * src_level)
        transferred = int(src_level * retention)
        dst_equip.refine_level = max(dst_equip.refine_level, transferred)
        src_equip.refine_level = 0
        return transferred

    def get_pity_count(self, eid: str) -> int:
        return self.fail_count.get(eid, 0)

    def get_material_type(self, slot: str, level: int) -> str:
        """材料按部位区分，高级精炼需要稀有材料。"""
        if level >= 10:
            return f"rare_{slot}_essence"
        if level >= 5:
            return f"{slot}_crystal"
        return f"{slot}_stone"

    def get_max_level(self) -> int:
        return MAX_REFINE_LEVEL

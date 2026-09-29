"""装备精炼与转移系统"""
from dataclasses import dataclass

MAX_REFINE_LEVEL = 15
PITY_THRESHOLD = 10          # 连续失败10次后必成功
DOWNGRADE_LEVEL = 7          # +7起失败会降级
BREAK_LEVEL = 12             # +12起失败有碎装备风险
BREAK_CHANCE = 0.3           # 高级精炼失败碎装备概率
RARE_MATERIAL_LEVEL = 10     # +10起需要稀有材料

# 按当前等级递减的成功率表（从level精炼到level+1）
SUCCESS_RATES = [
    0.95, 0.90, 0.85, 0.80, 0.75,
    0.70, 0.60, 0.50, 0.40, 0.30,
    0.10, 0.08, 0.06, 0.04, 0.02,
]


@dataclass
class Equipment:
    eid: str
    name: str
    refine_level: int = 0
    slot: str = "weapon"


class RefineSystem:
    failure_penalty_enabled = True
    can_downgrade = True
    can_break = True

    def __init__(self, seed=42):
        import random
        self.rng = random.Random(seed)
        self.equipment: dict[str, Equipment] = {}
        self.fail_count: dict[str, int] = {}
        self.materials: dict[str, int] = {}
        self.protection_charms: int = 0

    def get_success_rate(self, level: int) -> float:
        if level < 0 or level >= MAX_REFINE_LEVEL:
            return 0.0
        return SUCCESS_RATES[level]

    def get_max_level(self) -> int:
        return MAX_REFINE_LEVEL

    def get_pity_count(self, eid: str) -> int:
        return self.fail_count.get(eid, 0)

    def get_material_type(self, slot: str, level: int) -> str:
        grade = "rare" if level >= RARE_MATERIAL_LEVEL else "normal"
        return f"{slot}_{grade}_stone"

    def add_materials(self, material: str, count: int) -> None:
        self.materials[material] = self.materials.get(material, 0) + count

    def _consume_material(self, equip: Equipment) -> bool:
        material = self.get_material_type(equip.slot, equip.refine_level)
        if self.materials.get(material, 0) <= 0:
            return False
        self.materials[material] -= 1
        return True

    def refine(self, eid: str, use_protection: bool = False) -> tuple[bool, str]:
        equip = self.equipment[eid]
        if equip.refine_level >= MAX_REFINE_LEVEL:
            return False, "max_level"
        if not self._consume_material(equip):
            return False, "not_enough_material"

        protected = False
        if use_protection and self.protection_charms > 0:
            self.protection_charms -= 1
            protected = True

        pity_hit = self.fail_count.get(eid, 0) >= PITY_THRESHOLD
        success = pity_hit or self.rng.random() < self.get_success_rate(equip.refine_level)

        if success:
            equip.refine_level += 1
            self.fail_count[eid] = 0
            return True, "success"

        self.fail_count[eid] = self.fail_count.get(eid, 0) + 1
        if protected:
            return False, "failed_protected"
        if equip.refine_level >= BREAK_LEVEL and self.rng.random() < BREAK_CHANCE:
            del self.equipment[eid]
            self.fail_count.pop(eid, None)
            return False, "broken"
        if equip.refine_level >= DOWNGRADE_LEVEL:
            equip.refine_level -= 1
            return False, "downgraded"
        return False, "failed"

    def transfer_refine(self, src: str, dst: str) -> int:
        src_equip = self.equipment[src]
        dst_equip = self.equipment[dst]
        level = src_equip.refine_level
        # 按比例损耗，等级越高损耗越大（10%起步，最高50%）
        loss_rate = min(0.5, 0.1 + 0.03 * level)
        transferred = level - int(level * loss_rate + 0.999999)
        dst_equip.refine_level = min(transferred, MAX_REFINE_LEVEL)
        src_equip.refine_level = 0
        return dst_equip.refine_level

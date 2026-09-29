"""装备精炼与转移系统 - 含6个bug"""
from dataclasses import dataclass, field

@dataclass
class Equipment:
    eid: str
    name: str
    refine_level: int = 0
    slot: str = "weapon"

class RefineSystem:
    def __init__(self, seed=42):
        import random
        self.rng = random.Random(seed)
        self.equipment: dict[str, Equipment] = {}
        self.fail_count: dict[str, int] = {}  # bug4: 无保底

    def get_success_rate(self, level: int) -> float:
        # bug1: 固定成功率
        return 0.5

    def refine(self, eid: str) -> tuple[bool, str]:
        # bug2: 失败无惩罚
        equip = self.equipment[eid]
        if self.rng.random() < self.get_success_rate(equip.refine_level):
            equip.refine_level += 1
            return True, "success"
        return False, "failed"

    def transfer_refine(self, src: str, dst: str) -> int:
        # bug3: 100%转移
        src_equip = self.equipment[src]
        dst_equip = self.equipment[dst]
        dst_equip.refine_level = src_equip.refine_level
        return src_equip.refine_level

    def get_pity_count(self, eid: str) -> int:
        # bug4: 无保底
        return 0

    def get_material_type(self, slot: str, level: int) -> str:
        # bug5: 通用材料
        return "universal_stone"

    def get_max_level(self) -> int:
        # bug6: 无上限
        return 999

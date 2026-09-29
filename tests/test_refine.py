"""装备精炼与转移系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from equip.refine import RefineSystem, Equipment

class TestSuccessRate:
    def test_higher_level_lower_success_rate(self):
        rs = RefineSystem()
        r1 = rs.get_success_rate(1)
        r15 = rs.get_success_rate(15)
        assert r15 < r1  # bug1: 都是0.5

class TestFailurePenalty:
    def test_failed_refine_has_penalty(self):
        rs = RefineSystem(seed=1)
        rs.equipment["e1"] = Equipment("e1", "sword", refine_level=10)
        # 系统应该有失败惩罚机制
        assert hasattr(rs, "failure_penalty_enabled")
        # 连续失败应该有降级或碎装备风险
        assert hasattr(rs, "can_downgrade")

class TestTransferLoss:
    def test_transfer_has_loss(self):
        rs = RefineSystem()
        rs.equipment["src"] = Equipment("src", "old", refine_level=15)
        rs.equipment["dst"] = Equipment("dst", "new", refine_level=0)
        transferred = rs.transfer_refine("src", "dst")
        assert transferred < 15  # bug3: 100%转移=15

class TestPitySystem:
    def test_pity_increases_after_failures(self):
        rs = RefineSystem()
        rs.fail_count["e1"] = 10
        pity = rs.get_pity_count("e1")
        assert pity >= 10  # bug4: 0

class TestMaterialBySlot:
    def test_different_slots_use_different_materials(self):
        rs = RefineSystem()
        m1 = rs.get_material_type("weapon", 5)
        m2 = rs.get_material_type("armor", 5)
        assert m1 != m2  # bug5: 都是universal_stone

class TestMaxLevel:
    def test_refine_has_max_level(self):
        rs = RefineSystem()
        assert rs.get_max_level() < 30  # bug6: 999

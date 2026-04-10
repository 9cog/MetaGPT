#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/6/6 12:38
@Author  : alexanderwu
@File    : test_skill_manager.py
"""
import tempfile
from pathlib import Path

from metagpt.actions import WritePRD, WriteTest
from metagpt.logs import logger
from metagpt.management.skill_manager import SkillManager


def test_skill_manager():
    manager = SkillManager()
    logger.info(manager._store)

    write_prd = WritePRD(name="WritePRD")
    write_prd.desc = "基于老板或其他人的需求进行PRD的撰写，包括用户故事、需求分解等"
    write_test = WriteTest(name="WriteTest")
    write_test.desc = "进行测试用例的撰写"
    manager.add_skill(write_prd)
    manager.add_skill(write_test)

    skill = manager.get_skill("WriteTest")
    logger.info(skill)

    rsp = manager.retrieve_skill("WritePRD")
    logger.info(rsp)
    assert rsp[0] == "WritePRD"

    rsp = manager.retrieve_skill("写测试用例")
    logger.info(rsp)
    assert rsp[0] == "WriteTest"

    rsp = manager.retrieve_skill_scored("写PRD")
    logger.info(rsp)


def test_skill_manager_persistence():
    """Test that SkillManager can persist and load skills"""
    with tempfile.TemporaryDirectory() as tmpdir:
        persist_dir = Path(tmpdir) / "skills"
        
        # Create manager and add skills
        manager1 = SkillManager(persist_dir=persist_dir)
        write_prd = WritePRD(name="WritePRD")
        write_prd.desc = "Write PRD based on requirements"
        manager1.add_skill(write_prd)
        
        # Verify skill was persisted
        skill_file = persist_dir / "WritePRD.json"
        assert skill_file.exists()
        
        # Create new manager and verify it loads the skill
        manager2 = SkillManager(persist_dir=persist_dir)
        loaded_skill = manager2.get_skill("WritePRD")
        assert loaded_skill is not None
        assert loaded_skill.name == "WritePRD"
        
        # Test explicit persist
        write_test = WriteTest(name="WriteTest")
        write_test.desc = "Write test cases"
        manager2.add_skill(write_test)
        manager2.persist()
        
        # Verify both skills are persisted
        assert (persist_dir / "WritePRD.json").exists()
        assert (persist_dir / "WriteTest.json").exists()


def test_skill_manager_get_nonexistent():
    """get_skill() for an unknown name returns None rather than raising."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = SkillManager(persist_dir=Path(tmpdir) / "skills")
        result = manager.get_skill("NoSuchSkill")
        assert result is None


def test_skill_manager_del_skill():
    """del_skill() removes the skill from memory and from disk."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persist_dir = Path(tmpdir) / "skills"
        manager = SkillManager(persist_dir=persist_dir)

        write_prd = WritePRD(name="WritePRD")
        write_prd.desc = "Write PRD"
        manager.add_skill(write_prd)

        skill_file = persist_dir / "WritePRD.json"
        assert skill_file.exists()

        manager.del_skill("WritePRD")

        assert manager.get_skill("WritePRD") is None
        assert not skill_file.exists()


def test_skill_manager_type_preservation():
    """Skills loaded from disk should be reconstructed as their original class."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persist_dir = Path(tmpdir) / "skills"

        manager1 = SkillManager(persist_dir=persist_dir)
        write_prd = WritePRD(name="WritePRD")
        write_prd.desc = "Write PRD"
        manager1.add_skill(write_prd)

        manager2 = SkillManager(persist_dir=persist_dir)
        loaded = manager2.get_skill("WritePRD")
        assert loaded is not None
        assert isinstance(loaded, WritePRD)

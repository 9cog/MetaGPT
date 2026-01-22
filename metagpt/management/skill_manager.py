#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/6/5 01:44
@Author  : alexanderwu
@File    : skill_manager.py
@Modified By: mashenquan, 2023/8/20. Remove useless `llm`
"""
import json
from pathlib import Path

from metagpt.actions import Action
from metagpt.const import DATA_PATH, PROMPT_PATH
from metagpt.document_store.chromadb_store import ChromaStore
from metagpt.logs import logger

Skill = Action


class SkillManager:
    """Used to manage all skills with persistence support"""

    def __init__(self, persist_dir: Path = None):
        self._store = ChromaStore("skill_manager")
        self._skills: dict[str:Skill] = {}
        self.persist_dir = persist_dir or Path(DATA_PATH) / "skills"
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._load_skills()

    def add_skill(self, skill: Skill):
        """
        Add a skill, add the skill to the skill pool and searchable storage
        :param skill: Skill
        :return:
        """
        self._skills[skill.name] = skill
        self._store.add(skill.desc, {"name": skill.name, "desc": skill.desc}, skill.name)
        self._persist_skill(skill)

    def del_skill(self, skill_name: str):
        """
        Delete a skill, remove the skill from the skill pool and searchable storage
        :param skill_name: Skill name
        :return:
        """
        self._skills.pop(skill_name)
        self._store.delete(skill_name)
        # Delete persisted file
        skill_file = self.persist_dir / f"{skill_name}.json"
        if skill_file.exists():
            skill_file.unlink()

    def get_skill(self, skill_name: str) -> Skill:
        """
        Obtain a specific skill by skill name
        :param skill_name: Skill name
        :return: Skill
        """
        return self._skills.get(skill_name)

    def retrieve_skill(self, desc: str, n_results: int = 2) -> list[Skill]:
        """
        Obtain skills through the search engine
        :param desc: Skill description
        :return: Multiple skills
        """
        return self._store.search(desc, n_results=n_results)["ids"][0]

    def retrieve_skill_scored(self, desc: str, n_results: int = 2) -> dict:
        """
        Obtain skills through the search engine
        :param desc: Skill description
        :return: Dictionary consisting of skills and scores
        """
        return self._store.search(desc, n_results=n_results)

    def generate_skill_desc(self, skill: Skill) -> str:
        """
        Generate descriptive text for each skill
        :param skill:
        :return:
        """
        path = PROMPT_PATH / "generate_skill.md"
        text = path.read_text()
        logger.info(text)

    def _persist_skill(self, skill: Skill):
        """
        Persist a skill to disk
        :param skill: Skill to persist
        """
        try:
            skill_file = self.persist_dir / f"{skill.name}.json"
            skill_data = {
                "name": skill.name,
                "desc": skill.desc,
                "class_name": skill.__class__.__name__,
                "module": skill.__class__.__module__,
                # Store additional attributes as needed
            }
            with open(skill_file, 'w', encoding='utf-8') as f:
                json.dump(skill_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Persisted skill {skill.name} to {skill_file}")
        except Exception as e:
            logger.warning(f"Failed to persist skill {skill.name}: {e}")

    def _load_skills(self):
        """
        Load all persisted skills from disk
        """
        try:
            if not self.persist_dir.exists():
                return
            
            for skill_file in self.persist_dir.glob("*.json"):
                try:
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        skill_data = json.load(f)
                    
                    # Try to reconstruct the original skill class
                    # Note: Full reconstruction requires the class to be available in the module
                    try:
                        from metagpt.utils.common import import_class
                        skill_class = import_class(skill_data.get("class_name", "Action"), 
                                                   skill_data.get("module", "metagpt.actions"))
                        skill = skill_class(name=skill_data["name"], desc=skill_data.get("desc", ""))
                    except Exception:
                        # Fallback to basic Action if class cannot be imported
                        skill = Action(name=skill_data["name"], desc=skill_data.get("desc", ""))
                    
                    self._skills[skill.name] = skill
                    logger.info(f"Loaded skill {skill.name} from {skill_file}")
                except Exception as e:
                    logger.warning(f"Failed to load skill from {skill_file}: {e}")
        except Exception as e:
            logger.warning(f"Failed to load skills: {e}")

    def persist(self):
        """
        Persist all skills to disk
        """
        for skill in self._skills.values():
            self._persist_skill(skill)
        logger.info(f"Persisted {len(self._skills)} skills to {self.persist_dir}")


if __name__ == "__main__":
    manager = SkillManager()
    manager.generate_skill_desc(Action())

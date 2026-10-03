"""Tests for check_mob_ai_profiles.py.

The checker exists because the AI profile file once never loaded and every other
check passed. These pin the cases that were first proven by hand: a profile the
loader would reject, and a boot log showing the server never read the file."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))
import check_mob_ai_profiles as checker


def profile(**fields):
    base = {"Map": "orcsdun01", "Monster": "ORC_SKELETON", "Role": "Skirmisher", "HitThreshold": "3", "StepDistance": "3", "Cooldown": "5000"}
    base.update(fields)
    body = "\n".join(f"\t{key}: {value if str(value).isdigit() else chr(34) + str(value) + chr(34)}" for key, value in base.items())
    return "{\n" + body + "\n}"


class Fixture(unittest.TestCase):
    """Point the checker at a throwaway profile file and a one-monster mob_db."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        root = Path(self.dir.name)
        self.profiles = root / "profiles.conf"
        self.mobs = root / "mob_db.conf"
        self.mobs.write_text('mob_db: ( { SpriteName: "ORC_SKELETON" }, { SpriteName: "ORC_ARCHER" } )', encoding="utf-8")
        self._saved = (checker.PROFILES, checker.MOB_DB, checker.MAP_INDEX)
        checker.PROFILES = str(self.profiles)
        checker.MOB_DB = [str(self.mobs)]
        checker.MAP_INDEX = []  # no map list: skip the map check

    def tearDown(self):
        checker.PROFILES, checker.MOB_DB, checker.MAP_INDEX = self._saved
        self.dir.cleanup()

    def check(self, *blocks):
        self.profiles.write_text("\n".join(blocks), encoding="utf-8")
        problems = []
        valid = checker.check_profiles(problems)
        return valid, problems


class Profiles(Fixture):
    def test_a_valid_profile_is_counted_and_clean(self):
        self.assertEqual(self.check(profile()), (1, []))

    def test_a_threshold_outside_the_loaders_range_is_named(self):
        valid, problems = self.check(profile(HitThreshold="1"))
        self.assertEqual(valid, 0)
        self.assertIn("HitThreshold=1", problems[0])

    def test_an_unknown_monster_is_named(self):
        valid, problems = self.check(profile(Monster="NOT_A_MOB"))
        self.assertEqual(valid, 0)
        self.assertIn("NOT_A_MOB", problems[0])

    def test_a_missing_role_parameter_is_named(self):
        text = profile().replace('\tCooldown: 5000\n', "")
        valid, problems = self.check(text)
        self.assertEqual(valid, 0)
        self.assertIn("requires Cooldown", problems[0])

    def test_a_duplicate_map_and_monster_is_refused(self):
        valid, problems = self.check(profile(), profile())
        self.assertEqual(valid, 1)
        self.assertIn("duplicate", problems[0])

    def test_an_unknown_role_is_refused(self):
        valid, problems = self.check(profile(Role="Wizard"))
        self.assertEqual(valid, 0)
        self.assertIn("unknown role", problems[0])


class BootLog(unittest.TestCase):
    def run_log(self, text, expected=9):
        with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False, encoding="utf-8") as handle:
            handle.write(text)
        self.addCleanup(Path(handle.name).unlink)
        problems = []
        checker.check_boot_log(handle.name, expected, problems)
        return problems

    def test_a_server_that_never_found_the_file_is_the_bug_this_exists_for(self):
        problems = self.run_log("[Status]: No map-scoped mob AI profiles configured.\n")
        self.assertEqual(len(problems), 1)
        self.assertIn("NO profile file", problems[0])

    def test_a_server_that_read_fewer_profiles_than_the_file_holds_is_named(self):
        problems = self.run_log("[Status]: Read 3 map-scoped mob AI profiles from x\n")
        self.assertIn("read 3 profiles but the file has 9", problems[0])

    def test_a_server_that_read_every_profile_passes(self):
        self.assertEqual(self.run_log("[Status]: Read 9 map-scoped mob AI profiles from x\n"), [])

    def test_a_log_with_no_profile_line_at_all_fails(self):
        self.assertTrue(self.run_log("[Status]: nothing relevant\n"))

    def test_a_loader_warning_is_surfaced(self):
        problems = self.run_log("[Status]: Read 9 map-scoped mob AI profiles from x\n[Warning]: mob_ai_profile_db: invalid Skirmisher parameters for A on b; skipped.\n")
        self.assertEqual(len(problems), 1)


class RealFiles(unittest.TestCase):
    def test_this_servers_profiles_are_valid_and_the_switch_is_declared(self):
        problems = []
        valid = checker.check_profiles(problems)
        checker.check_switch(problems)
        self.assertEqual(problems, [])
        self.assertGreaterEqual(valid, 29)

    def test_expanded_boss_pilot_skills_are_valid_and_include_mvps(self):
        problems = []
        checker.check_pilot_skills(problems)
        self.assertEqual(problems, [])
        skills_text = checker.read(checker.PILOT_SKILLS)
        expected_bosses = (
            "EDDGA", "MOONLIGHT", "GOLDEN_BUG", "ORK_HERO", "MAYA", "BAPHOMET",
            "PHREEONI", "MISTRESS", "DRAKE", "DOPPELGANGER", "OSIRIS",
        )
        for boss in expected_bosses:
            self.assertIn(f"\t{boss}: {{", skills_text, f"{boss} must be configured in pilot skills")

    def test_tactical_profiles_cover_all_four_roles_and_progression_zones(self):
        entries = checker.parse_profiles(checker.read(checker.PROFILES))
        roles_present = {e["Role"].lower() for e in entries}
        self.assertEqual(roles_present, {"aggressor", "coward", "rangedkeeper", "skirmisher"})
        maps_present = {e["Map"].lower() for e in entries}
        expected_zones = {"prt_fild08", "prt_sewb1", "prt_sewb2", "prt_sewb3", "pay_dun00", "pay_dun01", "pay_dun02", "moc_fild01", "moc_fild12", "iz_dun00", "iz_dun01", "iz_dun02", "orcsdun01", "orcsdun02", "gl_knt01", "gl_prison"}
        for zone in expected_zones:
            self.assertIn(zone, maps_present, f"Zone {zone} must have tactical AI profile coverage")


if __name__ == "__main__":
    unittest.main()

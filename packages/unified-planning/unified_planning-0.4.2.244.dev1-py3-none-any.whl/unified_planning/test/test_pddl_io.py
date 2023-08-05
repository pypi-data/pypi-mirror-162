# Copyright 2021 AIPlan4EU project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

import os
import tempfile
from typing import cast
import pytest
import unified_planning
from unified_planning.shortcuts import *
from unified_planning.test import TestCase, main
from unified_planning.io import PDDLWriter, PDDLReader
from unified_planning.test.examples import get_example_problems
from unified_planning.model.types import _UserType


FILE_PATH = os.path.dirname(os.path.abspath(__file__))
PDDL_DOMAINS_PATH = os.path.join(FILE_PATH, "pddl")


class TestPddlIO(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.problems = get_example_problems()

    def test_basic_writer(self):
        problem = self.problems["basic"].problem

        w = PDDLWriter(problem)

        pddl_domain = w.get_domain()
        self.assertIn("(:requirements :strips :negative-preconditions)", pddl_domain)
        self.assertIn("(:predicates (x))", pddl_domain)
        self.assertIn("(:action a", pddl_domain)
        self.assertIn(":parameters ()", pddl_domain)
        self.assertIn(":precondition (and (not (x)))", pddl_domain)
        self.assertIn(":effect (and (x))", pddl_domain)

        pddl_problem = w.get_problem()
        self.assertIn("(:domain basic-domain)", pddl_problem)
        self.assertIn("(:init)", pddl_problem)
        self.assertIn("(:goal (and (x)))", pddl_problem)

    def test_basic_conditional_writer(self):
        problem = self.problems["basic_conditional"].problem

        self.assertTrue(problem.action("a_x").is_conditional())
        self.assertFalse(problem.action("a_y").is_conditional())

        w = PDDLWriter(problem)

        pddl_domain = w.get_domain()
        self.assertIn(
            "(:requirements :strips :negative-preconditions :conditional-effects)",
            pddl_domain,
        )
        self.assertIn("(:predicates (x) (y))", pddl_domain)
        self.assertIn("(:action a_x", pddl_domain)
        self.assertIn(":parameters ()", pddl_domain)
        self.assertIn(":precondition (and (not (x)))", pddl_domain)
        self.assertIn(":effect (and (when (y) (x)))", pddl_domain)
        self.assertIn("(:action a_y", pddl_domain)
        self.assertIn(":parameters ()", pddl_domain)
        self.assertIn(":precondition (and (not (y)))", pddl_domain)
        self.assertIn(":effect (and (y))", pddl_domain)

        pddl_problem = w.get_problem()
        self.assertIn("(:domain basic_conditional-domain)", pddl_problem)
        self.assertIn("(:init)", pddl_problem)
        self.assertIn("(:goal (and (x)))", pddl_problem)

    def test_basic_exists_writer(self):
        problem = self.problems["basic_exists"].problem

        w = PDDLWriter(problem)

        pddl_domain = w.get_domain()
        self.assertIn(
            "(:requirements :strips :typing :existential-preconditions)", pddl_domain
        )
        self.assertIn("(:predicates (x) (y ?semaphore - semaphore))", pddl_domain)
        self.assertIn("(:action a", pddl_domain)
        self.assertIn(":parameters ()", pddl_domain)
        self.assertIn(
            ":precondition (and (exists (?s - semaphore)\n (y ?s)))", pddl_domain
        )
        self.assertIn(":effect (and (x))", pddl_domain)

        pddl_problem = w.get_problem()
        self.assertIn("(:domain basic_exists-domain)", pddl_problem)
        self.assertIn("(:objects\n   o1 o2 - semaphore\n )", pddl_problem)
        self.assertIn("(:init (y o1))", pddl_problem)
        self.assertIn("(:goal (and (x)))", pddl_problem)

    def test_robot_writer(self):
        problem = self.problems["robot"].problem

        w = PDDLWriter(problem)

        pddl_domain = w.get_domain()
        self.assertIn(
            "(:requirements :strips :typing :negative-preconditions :equality :numeric-fluents)",
            pddl_domain,
        )
        self.assertIn("(:types location)", pddl_domain)
        self.assertIn("(:predicates (robot_at ?position - location))", pddl_domain)
        self.assertIn("(:functions (battery_charge))", pddl_domain)
        self.assertIn("(:action move", pddl_domain)
        self.assertIn(":parameters ( ?l_from - location ?l_to - location)", pddl_domain)
        self.assertIn(
            ":precondition (and (<= 10 (battery_charge)) (not (= ?l_from ?l_to)) (robot_at ?l_from) (not (robot_at ?l_to)))",
            pddl_domain,
        )
        self.assertIn(
            ":effect (and (not (robot_at ?l_from)) (robot_at ?l_to) (assign (battery_charge) (- (battery_charge) 10)))",
            pddl_domain,
        )

        pddl_problem = w.get_problem()
        self.assertIn("(:domain robot-domain)", pddl_problem)
        self.assertIn("(:objects", pddl_problem)
        self.assertIn("l1 l2 - location", pddl_problem)
        self.assertIn("(:init (robot_at l1) (= (battery_charge) 100))", pddl_problem)
        self.assertIn("(:goal (and (robot_at l2)))", pddl_problem)

    def test_robot_decrease_writer(self):
        problem = self.problems["robot_decrease"].problem

        w = PDDLWriter(problem)

        pddl_domain = w.get_domain()
        self.assertIn(
            "(:requirements :strips :typing :negative-preconditions :equality :numeric-fluents)",
            pddl_domain,
        )
        self.assertIn("(:types location)", pddl_domain)
        self.assertIn("(:predicates (robot_at ?position - location))", pddl_domain)
        self.assertIn("(:functions (battery_charge))", pddl_domain)
        self.assertIn("(:action move", pddl_domain)
        self.assertIn(":parameters ( ?l_from - location ?l_to - location)", pddl_domain)
        self.assertIn(
            ":precondition (and (<= 10 (battery_charge)) (not (= ?l_from ?l_to)) (robot_at ?l_from) (not (robot_at ?l_to)))",
            pddl_domain,
        )
        self.assertIn(
            ":effect (and (not (robot_at ?l_from)) (robot_at ?l_to) (decrease (battery_charge) 10))",
            pddl_domain,
        )

        pddl_problem = w.get_problem()
        self.assertIn("(:domain robot_decrease-domain)", pddl_problem)
        self.assertIn("(:objects", pddl_problem)
        self.assertIn("l1 l2 - location", pddl_problem)
        self.assertIn("(:init (robot_at l1) (= (battery_charge) 100))", pddl_problem)
        self.assertIn("(:goal (and (robot_at l2)))", pddl_problem)

    def test_robot_loader_writer(self):
        problem = self.problems["robot_loader"].problem

        w = PDDLWriter(problem)

        pddl_domain = w.get_domain()
        self.assertIn(
            "(:requirements :strips :typing :negative-preconditions :equality)",
            pddl_domain,
        )
        self.assertIn("(:types location)", pddl_domain)
        self.assertIn(
            "(:predicates (robot_at ?position - location) (cargo_at ?position - location) (cargo_mounted))",
            pddl_domain,
        )
        self.assertIn("(:action move", pddl_domain)
        self.assertIn(":parameters ( ?l_from - location ?l_to - location)", pddl_domain)
        self.assertIn(
            ":precondition (and (not (= ?l_from ?l_to)) (robot_at ?l_from) (not (robot_at ?l_to)))",
            pddl_domain,
        )
        self.assertIn(
            ":effect (and (not (robot_at ?l_from)) (robot_at ?l_to))", pddl_domain
        )
        self.assertIn("(:action load", pddl_domain)
        self.assertIn(":parameters ( ?loc - location)", pddl_domain)
        self.assertIn(
            ":precondition (and (cargo_at ?loc) (robot_at ?loc) (not (cargo_mounted)))",
            pddl_domain,
        )
        self.assertIn(
            ":effect (and (not (cargo_at ?loc)) (cargo_mounted))", pddl_domain
        )
        self.assertIn("(:action unload", pddl_domain)
        self.assertIn(":parameters ( ?loc - location)", pddl_domain)
        self.assertIn(
            ":precondition (and (not (cargo_at ?loc)) (robot_at ?loc) (cargo_mounted))",
            pddl_domain,
        )
        self.assertIn(
            ":effect (and (cargo_at ?loc) (not (cargo_mounted)))", pddl_domain
        )

        pddl_problem = w.get_problem()
        self.assertIn("(:domain robot_loader-domain)", pddl_problem)
        self.assertIn("(:objects", pddl_problem)
        self.assertIn("l1 l2 - location", pddl_problem)
        self.assertIn("(:init (robot_at l1) (cargo_at l2))", pddl_problem)
        self.assertIn("(:goal (and (cargo_at l1)))", pddl_problem)

    def test_robot_loader_adv_writer(self):
        problem = self.problems["robot_loader_adv"].problem

        w = PDDLWriter(problem)

        pddl_domain = w.get_domain()
        self.assertIn(
            "(:requirements :strips :typing :negative-preconditions :equality)",
            pddl_domain,
        )
        self.assertIn("(:types robot location container)", pddl_domain)
        self.assertIn(
            "(:predicates (robot_at ?robot - robot ?position - location) (cargo_at ?cargo - container ?position - location) (cargo_mounted ?cargo - container ?robot - robot))",
            pddl_domain,
        )
        self.assertIn("(:action move", pddl_domain)
        self.assertIn(
            ":parameters ( ?l_from - location ?l_to - location ?r - robot)", pddl_domain
        )
        self.assertIn(
            ":precondition (and (not (= ?l_from ?l_to)) (robot_at ?r ?l_from) (not (robot_at ?r ?l_to)))",
            pddl_domain,
        )
        self.assertIn(
            ":effect (and (not (robot_at ?r ?l_from)) (robot_at ?r ?l_to))", pddl_domain
        )
        self.assertIn("(:action load", pddl_domain)
        self.assertIn(
            ":parameters ( ?loc - location ?r - robot ?c - container)", pddl_domain
        )
        self.assertIn(
            ":precondition (and (cargo_at ?c ?loc) (robot_at ?r ?loc) (not (cargo_mounted ?c ?r)))",
            pddl_domain,
        )
        self.assertIn(
            ":effect (and (not (cargo_at ?c ?loc)) (cargo_mounted ?c ?r))", pddl_domain
        )
        self.assertIn("(:action unload", pddl_domain)
        self.assertIn(
            ":parameters ( ?loc - location ?r - robot ?c - container)", pddl_domain
        )
        self.assertIn(
            ":precondition (and (not (cargo_at ?c ?loc)) (robot_at ?r ?loc) (cargo_mounted ?c ?r))",
            pddl_domain,
        )
        self.assertIn(
            ":effect (and (cargo_at ?c ?loc) (not (cargo_mounted ?c ?r)))", pddl_domain
        )

        pddl_problem = w.get_problem()
        self.assertIn("(:domain robot_loader_adv-domain)", pddl_problem)
        self.assertIn("(:objects", pddl_problem)
        self.assertIn("r1 - robot", pddl_problem)
        self.assertIn("l1 l2 l3 - location", pddl_problem)
        self.assertIn("c1 - container", pddl_problem)
        self.assertIn("(:init (robot_at r1 l1) (cargo_at c1 l2))", pddl_problem)
        self.assertIn("(:goal (and (cargo_at c1 l3) (robot_at r1 l1)))", pddl_problem)

    def test_matchcellar_writer(self):
        problem = self.problems["matchcellar"].problem

        w = PDDLWriter(problem)

        pddl_domain = w.get_domain()
        self.assertIn("(define (domain matchcellar-domain)", pddl_domain)
        self.assertIn(
            "(:requirements :strips :typing :negative-preconditions :durative-actions)",
            pddl_domain,
        )
        self.assertIn("(:types match fuse)", pddl_domain)
        self.assertIn(
            "(:predicates (handfree) (light) (match_used ?match - match) (fuse_mended ?fuse - fuse))",
            pddl_domain,
        )
        self.assertIn("(:durative-action light_match", pddl_domain)
        self.assertIn(":parameters ( ?m - match)", pddl_domain)
        self.assertIn(":duration (= ?duration 6)", pddl_domain)
        self.assertIn(":condition (and (at start (not (match_used ?m))))", pddl_domain)
        self.assertIn(
            ":effect (and (at start (match_used ?m)) (at start (light)) (at end (not (light)))))",
            pddl_domain,
        )
        self.assertIn("(:durative-action mend_fuse", pddl_domain)
        self.assertIn(":parameters ( ?f - fuse)", pddl_domain)
        self.assertIn(":duration (= ?duration 5)", pddl_domain)
        self.assertIn(
            ":condition (and (at start (handfree))(at start (light))(over all (light))(at end (light)))",
            pddl_domain,
        )
        self.assertIn(
            ":effect (and (at start (not (handfree))) (at end (fuse_mended ?f)) (at end (handfree))))",
            pddl_domain,
        )

    def test_depot_reader(self):
        reader = PDDLReader()

        domain_filename = os.path.join(PDDL_DOMAINS_PATH, "depot", "domain.pddl")
        problem_filename = os.path.join(PDDL_DOMAINS_PATH, "depot", "problem.pddl")
        problem = reader.parse_problem(domain_filename, problem_filename)

        self.assertTrue(problem is not None)
        self.assertEqual(len(problem.fluents), 15)
        self.assertEqual(len(problem.actions), 5)
        self.assertEqual(len(list(problem.objects(problem.user_type("object")))), 13)

    def test_counters_reader(self):
        reader = PDDLReader()

        domain_filename = os.path.join(PDDL_DOMAINS_PATH, "counters", "domain.pddl")
        problem_filename = os.path.join(PDDL_DOMAINS_PATH, "counters", "problem.pddl")
        problem = reader.parse_problem(domain_filename, problem_filename)

        self.assertTrue(problem is not None)
        self.assertEqual(len(problem.fluents), 2)
        self.assertEqual(len(problem.actions), 2)
        self.assertEqual(len(list(problem.objects(problem.user_type("counter")))), 4)

    def test_sailing_reader(self):
        reader = PDDLReader()

        domain_filename = os.path.join(PDDL_DOMAINS_PATH, "sailing", "domain.pddl")
        problem_filename = os.path.join(PDDL_DOMAINS_PATH, "sailing", "problem.pddl")
        problem = reader.parse_problem(domain_filename, problem_filename)

        self.assertTrue(problem is not None)
        self.assertEqual(len(problem.fluents), 4)
        self.assertEqual(len(problem.actions), 8)
        self.assertEqual(len(list(problem.objects(problem.user_type("boat")))), 2)
        self.assertEqual(len(list(problem.objects(problem.user_type("person")))), 2)

    def test_matchcellar_reader(self):
        reader = PDDLReader()

        domain_filename = os.path.join(PDDL_DOMAINS_PATH, "matchcellar", "domain.pddl")
        problem_filename = os.path.join(
            PDDL_DOMAINS_PATH, "matchcellar", "problem.pddl"
        )
        problem = reader.parse_problem(domain_filename, problem_filename)

        self.assertTrue(problem is not None)
        self.assertEqual(len(problem.fluents), 4)
        self.assertEqual(len(problem.actions), 2)
        self.assertEqual(len(list(problem.objects(problem.user_type("match")))), 3)
        self.assertEqual(len(list(problem.objects(problem.user_type("fuse")))), 3)

    def test_htn_transport_reader(self):
        reader = PDDLReader()

        domain_filename = os.path.join(
            PDDL_DOMAINS_PATH, "htn-transport", "domain.hddl"
        )
        problem_filename = os.path.join(
            PDDL_DOMAINS_PATH, "htn-transport", "problem.hddl"
        )
        problem = reader.parse_problem(domain_filename, problem_filename)

        assert isinstance(problem, up.model.htn.HierarchicalProblem)
        self.assertEqual(5, len(problem.fluents))
        self.assertEqual(4, len(problem.actions))
        self.assertEqual(
            ["deliver", "get-to", "load", "unload"],
            [task.name for task in problem.tasks],
        )
        self.assertEqual(
            [
                "m-deliver",
                "m-unload",
                "m-load",
                "m-drive-to",
                "m-drive-to-via",
                "m-i-am-there",
            ],
            [method.name for method in problem.methods],
        )
        self.assertEqual(1, len(problem.method("m-drive-to").subtasks))
        self.assertEqual(2, len(problem.method("m-drive-to-via").subtasks))
        self.assertEqual(2, len(problem.task_network.subtasks))

    def test_examples_io(self):
        for example in self.problems.values():
            problem = example.problem
            kind = problem.kind
            if (
                kind.has_intermediate_conditions_and_effects()
                or kind.has_object_fluents()
                or kind.has_oversubscription()
            ):
                continue
            with tempfile.TemporaryDirectory() as tempdir:
                domain_filename = os.path.join(tempdir, "domain.pddl")
                problem_filename = os.path.join(tempdir, "problem.pddl")

                w = PDDLWriter(problem)
                w.write_domain(domain_filename)
                w.write_problem(problem_filename)

                reader = PDDLReader()
                parsed_problem = reader.parse_problem(domain_filename, problem_filename)

                self.assertEqual(len(problem.fluents), len(parsed_problem.fluents))
                self.assertTrue(
                    _have_same_user_types_considering_renamings(
                        problem, parsed_problem, w.get_item_named
                    )
                )
                self.assertEqual(len(problem.actions), len(parsed_problem.actions))
                for a in problem.actions:
                    parsed_a = parsed_problem.action(w.get_pddl_name(a))
                    self.assertEqual(a, w.get_item_named(parsed_a.name))
                    for param, parsed_param in zip(a.parameters, parsed_a.parameters):
                        self.assertEqual(
                            param.type, w.get_item_named(parsed_param.type.name)
                        )
                    if isinstance(a, unified_planning.model.InstantaneousAction):
                        self.assertEqual(len(a.effects), len(parsed_a.effects))
                    elif isinstance(a, unified_planning.model.DurativeAction):
                        self.assertEqual(str(a.duration), str(parsed_a.duration))
                        for t, e in a.effects.items():
                            self.assertEqual(len(e), len(parsed_a.effects[t]))

    def test_basic_with_object_constant(self):
        problem = self.problems["basic_with_object_constant"].problem

        w = PDDLWriter(problem)

        pddl_domain = w.get_domain()
        pddl_problem = w.get_problem()

        expected_domain = """(define (domain basic_with_object_constant-domain)
 (:requirements :strips :typing :negative-preconditions)
 (:types location)
 (:constants
   l1 - location
 )
 (:predicates (is_at ?loc - location))
 (:action move
  :parameters ( ?l_from - location ?l_to - location)
  :precondition (and (is_at ?l_from) (not (is_at ?l_to)))
  :effect (and (not (is_at ?l_from)) (is_at ?l_to)))
 (:action move_to_l1
  :parameters ( ?l_from - location)
  :precondition (and (is_at ?l_from) (not (is_at l1)))
  :effect (and (not (is_at ?l_from)) (is_at l1)))
)
"""
        expected_problem = """(define (problem basic_with_object_constant-problem)
 (:domain basic_with_object_constant-domain)
 (:objects
   l2 - location
 )
 (:init (is_at l1))
 (:goal (and (is_at l2)))
)
"""
        self.assertEqual(pddl_domain, expected_domain)
        self.assertEqual(pddl_problem, expected_problem)

    def test_rationals(self):
        problem = self.problems["robot_decrease"].problem.clone()

        # Check perfect conversion
        battery = problem.fluent("battery_charge")
        problem.set_initial_value(battery, Fraction(5, 2))
        w = PDDLWriter(problem)
        pddl_txt = w.get_problem()
        self.assertNotIn("5/2", pddl_txt)
        self.assertIn("2.5", pddl_txt)

        # Check imperfect conversion
        with pytest.warns(UserWarning, match="cannot exactly represent") as warns:
            battery = problem.fluent("battery_charge")
            problem.set_initial_value(battery, Fraction(10, 3))
            w = PDDLWriter(problem)
            pddl_txt = w.get_problem()
            self.assertNotIn("10/3", pddl_txt)
            self.assertIn("3.333333333", pddl_txt)

    def test_ad_hoc_1(self):
        when = UserType("when")
        fl = Fluent("4ction")
        obj_1 = Object("obj_1", when)
        obj_2 = Object("OBJ_1", when)
        act = InstantaneousAction("forall", AND=when)
        fluent = act.parameter("AND")
        act.add_effect(fl, True, Equals(fluent, obj_1))
        problem = Problem("ad_hoc")
        problem.add_fluent(fl)
        problem.add_action(act)
        problem.add_object(obj_1)
        problem.add_object(obj_2)
        problem.set_initial_value(fl, False)
        w = PDDLWriter(problem)
        pddl_domain = w.get_domain()
        pddl_problem = w.get_problem()
        expected_domain = """(define (domain ad_hoc-domain)
 (:requirements :strips :typing :equality :conditional-effects)
 (:types when_)
 (:constants
   obj_1 - when_
 )
 (:predicates (f_4ction))
 (:action forall_
  :parameters ( ?and_ - when_)
  :effect (and (when (= ?and_ obj_1) (f_4ction))))
)
"""
        expected_problem = """(define (problem ad_hoc-problem)
 (:domain ad_hoc-domain)
 (:objects
   obj_1_0 - when_
 )
 (:init)
 (:goal (and ))
)
"""
        self.assertEqual(pddl_domain, expected_domain)
        self.assertEqual(pddl_problem, expected_problem)

    def test_miconic_reader(self):
        reader = PDDLReader()

        domain_filename = os.path.join(PDDL_DOMAINS_PATH, "miconic", "domain.pddl")
        problem_filename = os.path.join(PDDL_DOMAINS_PATH, "miconic", "problem.pddl")
        problem = reader.parse_problem(domain_filename, problem_filename)

        self.assertTrue(problem is not None)
        self.assertEqual(len(problem.fluents), 15)
        self.assertEqual(len(problem.actions), 3)
        self.assertEqual(len(list(problem.objects(problem.user_type("passenger")))), 2)
        self.assertEqual(len(list(problem.objects(problem.user_type("floor")))), 4)

    def test_citycar_reader(self):
        reader = PDDLReader()

        domain_filename = os.path.join(PDDL_DOMAINS_PATH, "citycar", "domain.pddl")
        problem_filename = os.path.join(PDDL_DOMAINS_PATH, "citycar", "problem.pddl")
        problem = reader.parse_problem(domain_filename, problem_filename)

        self.assertTrue(problem is not None)
        self.assertEqual(len(problem.fluents), 10)
        self.assertEqual(len(problem.actions), 7)
        self.assertEqual(len(list(problem.objects(problem.user_type("junction")))), 9)
        self.assertEqual(len(list(problem.objects(problem.user_type("car")))), 2)
        self.assertEqual(len(list(problem.objects(problem.user_type("garage")))), 3)
        self.assertEqual(len(list(problem.objects(problem.user_type("road")))), 5)

    def test_robot_fastener_reader(self):
        reader = PDDLReader()

        domain_filename = os.path.join(
            PDDL_DOMAINS_PATH, "robot_fastener", "domain.pddl"
        )
        problem_filename = os.path.join(
            PDDL_DOMAINS_PATH, "robot_fastener", "problem.pddl"
        )
        problem = reader.parse_problem(domain_filename, problem_filename)

        self.assertTrue(problem is not None)
        self.assertEqual(len(problem.fluents), 5)
        self.assertEqual(len(problem.actions), 1)
        self.assertEqual(len(list(problem.objects(problem.user_type("robot")))), 3)
        self.assertEqual(len(list(problem.objects(problem.user_type("fastener")))), 3)

    def test_safe_road_reader(self):
        reader = PDDLReader()

        domain_filename = os.path.join(PDDL_DOMAINS_PATH, "safe_road", "domain.pddl")
        problem_filename = os.path.join(PDDL_DOMAINS_PATH, "safe_road", "problem.pddl")
        problem = reader.parse_problem(domain_filename, problem_filename)

        self.assertTrue(problem is not None)
        self.assertEqual(len(problem.fluents), 1)
        self.assertEqual(len(problem.actions), 2)
        natural_disaster = problem.action("natural_disaster")
        # 9 effects because the forall is expanded in 3 * 3 possible locations instantiations
        self.assertEqual(len(natural_disaster.effects), 9)
        self.assertEqual(len(list(problem.objects(problem.user_type("location")))), 3)


def _have_same_user_types_considering_renamings(
    original_problem: unified_planning.model.Problem,
    tested_problem: unified_planning.model.Problem,
    get_item_named,
) -> bool:
    for tested_type in tested_problem.user_types:
        if (
            get_item_named(cast(_UserType, tested_type).name)
            not in original_problem.user_types
        ):
            return False
    return True

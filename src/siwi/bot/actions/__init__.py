import importlib
import siwi
import yaml


class SiwiActions():
    def __init__(self) -> None:
        self.intent_map = {}
        self.load_data()

    def load_data(self) -> None:
        # load data from yaml files
        module_path = f"{ siwi.__path__[0] }/bot/test/data"

        with open(f"{ module_path }/example_intents.yaml", "r") as file:
            self.intent_map = yaml.safe_load(file)["intents"]

    def get(self, intent: dict):
        """
        returns SiwiActionBase
        """
        if len(intent["intents"]) > 0:
            intent_name = intent["intents"][0]
        else:
            intent_name = "fallback"

        cls_name = self.intent_map.get(intent_name).get("action")
        action_cls = getattr(
            importlib.import_module("siwi.bot.actions"), cls_name)
        action = action_cls(intent)
        return action


class SiwiActionBase():
    def __init__(self, intent: dict):
        """
        intent:
        {
            "entities": entities,
            "intents": intents
        }
        """
        self.load_test_data()
        self.error = False

    def load_test_data(self) -> None:
        module_path = f"{ siwi.__path__[0] }/bot/test/data"

        with open(f"{ module_path }/example_players.yaml", "r") as file:
            self.players = yaml.safe_load(file)

        with open(f"{ module_path }/example_teams.yaml", "r") as file:
            self.teams = yaml.safe_load(file)

        self.player_names = {
            value: key for (key, value) in self.players.items()
            }
        self.team_names = {
            value: key for (key, value) in self.teams.items()
            }

    def _name(self, vid: str) -> str:
        if vid.startswith("player"):
            return self.player_names.get(vid, "unknown player")
        elif vid.startswith("team"):
            return self.team_names.get(vid, "unkonwn team")
        else:
            return "unkonwn"

    def _vid(self, name: str) -> str:
        if name in self.players:
            return self.players[name]
        elif name in self.teams:
            return self.teams[name]
        else:
            print(
                f"[ERROR] Something went wrong, unknown vertex name { name }")
            raise

    def _error_check(self):
        if self.error:
            return "Opps, something went wrong."


class FallbackAction(SiwiActionBase):
    def __init__(self, intent):
        super().__init__(intent)

    def execute(self, connection_pool=None):
        """
        TBD: query some information via nbi_api in fallback case:
        https://github.com/swar/nba_api/blob/master/docs/examples/Basics.ipynb
        """
        return """
Sorry I don't understand your questions for now.
Here are supported question patterns:

relation:
    - What is the relationship between Yao Ming and Lakers?
    - How does Yao Ming and Lakers connected?
serving:
    - Which team had Yao Ming served?
friendship:
    - Whom does Tim Duncan follow?
    - Who are Yao Ming's friends?
"""


class RelationshipAction(SiwiActionBase):
    """
    USE basketballplayer;
    FIND NOLOOP PATH
    FROM "player100" TO "team204" OVER * BIDIRECT UPTO 4 STEPS YIELD path AS p;
    """
    def __init__(self, intent):
        print(f"[DEBUG] RelationshipAction intent: { intent }")
        super().__init__(intent)
        try:
            self.entity_left, self.entity_right = intent["entities"]
            self.left_vid = self._vid(self.entity_left)
            self.right_vid = self._vid(self.entity_right)
        except Exception:
            print(
                f"[WARN] RelationshipAction entities recognition Failure "
                f"will fallback to FallbackAction, "
                f"intent: { intent }"
                )
            self.error = True

    def execute(self, connection_pool) -> str:
        self._error_check()
        query = (
            f'USE basketballplayer;'
            f'FIND NOLOOP PATH '
            f'FROM "{self.left_vid}" TO "{self.right_vid}" '
            f'OVER * BIDIRECT UPTO 4 STEPS YIELD path AS p;'
            )
        print(
            f"[DEBUG] query for RelationshipAction :\n\t{ query }"
            )
        with connection_pool.session_context("root", "nebula") as session:
            result = session.execute(query)

        if not result.is_succeeded():
            return (
                f"Something is wrong on Graph Database connection when query "
                f"{ query }"
                )

        if result.is_empty():
            return (
                f"There is no relationship between "
                f"{ self.entity_left } and { self.entity_right }"
                )
        path = result.row_values(0)[0].as_path()
        relationships = path.relationships()
        relations_str = self._name(
            relationships[0].start_vertex_id().as_string())
        for rel_index in range(path.length()):
            rel = relationships[rel_index]
            relations_str += (
                f" { rel.edge_name() }s "
                f"{ self._name(rel.end_vertex_id().as_string()) }")
        return (
            f"There are at least { result.row_size() } relations between "
            f"{ self.entity_left } and { self.entity_right }, "
            f"one relation path is: { relations_str }."
            )


class ServeAction(SiwiActionBase):
    """
    USE basketballplayer;
    MATCH p=(v)-[e:serve*1]->(v1)
    WHERE id(v) == "player133"
         RETURN p LIMIT 100
    """
    def __init__(self, intent):
        print(f"[DEBUG] ServeAction intent: { intent }")
        super().__init__(intent)
        try:
            self.player0 = list(intent["entities"].keys())[0]
            self.player0_vid = self._vid(self.player0)
        except Exception:
            print(
                f"[WARN] ServeAction entities recognition Failure "
                f"will fallback to FallbackAction, "
                f"intent: { intent }"
                )
            self.error = True

    def execute(self, connection_pool) -> str:
        self._error_check()
        query = (
            f'USE basketballplayer;'
            f'MATCH p=(v)-[e:serve*1]->(v1) '
            f'WHERE id(v) == "{ self.player0_vid }" '
            f'    RETURN p LIMIT 100;'
            )
        print(
            f"[DEBUG] query for RelationshipAction :\n\t{ query }"
            )
        with connection_pool.session_context("root", "nebula") as session:
            result = session.execute(query)

        if not result.is_succeeded():
            return (
                f"Something is wrong on Graph Database connection when query "
                f"{ query }"
                )

        if result.is_empty():
            return (
                f"There is no teams served by "
                f"{ self.player0 }"
                )
        serving_teams_str = ""
        for index in range(result.row_size()):
            rel = result.row_values(index)[0].as_path().relationships()[0]
            serving_teams_str += (
                f"{ self._name(rel.end_vertex_id().as_string()) } "
                f"from { rel.properties()['start_year'] } "
                f"to { rel.properties()['start_year'] }; "
                )
        return (
            f"{ self.player0 } had served { result.row_size() } team"
            f"{'s' if result.row_size() > 1 else ''}. "
            f"{ serving_teams_str }"
            )


class FollowAction(SiwiActionBase):
    """
    USE basketballplayer;
    MATCH p=(v)-[e:follow*1]->(v1)
    WHERE id(v) == "player133"
         RETURN p LIMIT 100
    """
    def __init__(self, intent):
        print(f"[DEBUG] FollowAction intent: { intent }")
        super().__init__(intent)
        try:
            self.player0 = list(intent["entities"].keys())[0]
            self.player0_vid = self._vid(self.player0)
        except Exception:
            print(
                f"[WARN] ServeAction entities recognition Failure "
                f"will fallback to FallbackAction, "
                f"intent: { intent }"
                )
            self.error = True

    def execute(self, connection_pool) -> str:
        self._error_check()
        query = (
            f'USE basketballplayer;'
            f'MATCH p=(v)-[e:follow*1]->(v1) '
            f'WHERE id(v) == "{ self.player0_vid }" '
            f'    RETURN p LIMIT 100;'
            )
        print(
            f"[DEBUG] query for RelationshipAction :\n\t{ query }"
            )
        with connection_pool.session_context("root", "nebula") as session:
            result = session.execute(query)

        if not result.is_succeeded():
            return (
                f"Something is wrong on Graph Database connection when query "
                f"{ query }"
                )

        if result.is_empty():
            return (
                f"There is no players followed by "
                f"{ self.player0 }"
                )
        following_players_str = ""
        for index in range(result.row_size()):
            rel = result.row_values(index)[0].as_path().relationships()[0]
            following_players_str += (
                f"{ self._name(rel.end_vertex_id().as_string()) } "
                f"in degree { rel.properties()['degree'] }; "
                )
        return (
            f"{ self.player0 } had followed { result.row_size() } player"
            f"{'s' if result.row_size() > 1 else ''}. "
            f"{ following_players_str }"
            )

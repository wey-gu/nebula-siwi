import yaml


class SiwiActionBase():
    def __init__(self, intent):
        self.load_test_data()

    def load_test_data(self):
        module_path = f"{ siwi.__path__ }/bot/test/data"

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


    def _name(self, vid):
        if vid.startswith("player"):
            return self.player_names.get(vid, "unknown player")
        elif vid.startswith("team"):
            return self.player_names.get(vid, "unkonwn team")
        else:
            return "unkonwn"

    def _vid(self, name):
        if name in self.players:
            return self.players[name]
        elif name in self.teams:
            return self.teams[name]
        else:
            print(f"[ERROR] Something went wrong, unknown vertex name { name }")
            raise


class FallbackAction(SiwiActionBase):
    def __init__(self, intent):
        super().__init__()

    def execute(self):
        # query some information via nbi_api
        # https://github.com/swar/nba_api/blob/master/docs/examples/Basics.ipynb
        pass


class RelationshipAction(SiwiActionBase):
    """
    # with connection_pool.session_context("root", "nebula") as session:
    #     query = (
    #         f'USE basketballplayer;'
    #         f'FIND NOLOOP PATH '
    #         f'FROM "player100" TO "team204" OVER * BIDIRECT UPTO 3 STEPS;'
    #         )
    #     result = session.execute(query)
    """
    def __init__(self, intent):
        super().__init__()
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
            return FallbackAction(intent)

    def execute(self, connection_pool):
        with connection_pool.session_context("root", "nebula") as session:
            query = (
                f'USE basketballplayer;'
                f'FIND NOLOOP PATH '
                f'FROM "{self.left_vid}" TO "{self.right_vid}" '
                f'OVER * BIDIRECT UPTO 3 STEPS;'
                )

            result = session.execute(query)

        if not result.is_succeeded():
            return (
                f"Something is wrong on Graph Database connection when querying "
                f"{self.entity_left} and {self.entity_right}"
                )

        if result.is_empty():
            return (
                f"There is no relationship between "
                f"{self.entity_left} and {self.entity_right}"
                )
        path = result.row_values(0)[0].as_path()
        relationships = path.relationships()
        relations_str = self._name(relationships[0].start_vertex_id())
        for rel_index in range(path.length()):
            rel = relationships[rel_index]
            relations_str += f"{ rel.edge_name() }s { rel.end_vertex_id() }"
        return (
            f"There are at least { result.row_size() } relations between "
            f"{self.entity_left} and {self.entity_right}, "
            f"the relation path is: { relations_str }."
            )


class ServeAction(SiwiActionBase):
    pass


class FollowAction(SiwiActionBase):
    pass


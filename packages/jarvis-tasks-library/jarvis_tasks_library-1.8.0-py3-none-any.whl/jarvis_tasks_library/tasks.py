import json
from typing import Any


class Tasks:

    # Redis constants
    PREFIX = "task"
    MAX_KEY = "maxKey::" + PREFIX
    SCHEMA = {
        "name": "string",
        "time": "string",
        "active": "bool",
        "is_one_time": "bool",
        "notify": "bool",
    }

    # AC Master
    TURN_ON_COOLING_MASTER = "turn-on-cooling-master"
    TURN_ON_HEAT_MASTER = "turn-on-heat-master"
    TURN_OFF_AC_MASTER = "turn-off-ac-master"

    # AC JF
    TURN_ON_COOLING_JF = "turn-on-cooling-jf"
    TURN_ON_HEAT_JF = "turn-on-heat-jf"
    TURN_OFF_AC_JF = "turn-off-ac-jf"

    # Smart lock
    OPEN_SMART_LOCK = "open-smart-lock"
    CLOSE_SMART_LOCK = "close-smart-lock"

    # Alarm
    ARM_ALARM = "arm-alarm"
    DISARM_ALARM = "disarm-alarm"

    # Home
    # Irrigation
    HOME_OPEN_IRRIGATION = "home-open-irrigation"
    HOME_CLOSE_IRRIGATION = "home-close-irrigation"
    # Pool Pump
    HOME_TURN_ON_POOL_PUMP = "home-turn-on-pool-pump"
    HOME_TURN_OFF_POOL_PUMP = "home-turn-off-pool-pump"
    # Pool water
    HOME_OPEN_POOL_WATER = "home-open-pool-water"
    HOME_CLOSE_POOL_WATER = "home-close-pool-water"
    # Bar Pump
    HOME_TURN_ON_BAR_PUMP = "home-turn-on-bar-pump"
    HOME_TURN_OFF_BAR_PUMP = "home-turn-off-bar-pump"
    # Front lights
    HOME_TURN_ON_FRONT_LIGHTS = "home-turn-on-front-lights"
    HOME_TURN_OFF_FRONT_LIGHTS = "home-turn-off-front-lights"
    # Front spot lights
    HOME_TURN_ON_FRONT_SPOT_LIGHTS = "home-turn-on-front-spot-lights"
    HOME_TURN_OFF_FRONT_SPOT_LIGHTS = "home-turn-off-front-spot-lights"
    # Back Main lights
    HOME_TURN_ON_BACK_LIGHTS = "home-turn-on-back-lights"
    HOME_TURN_OFF_BACK_LIGHTS = "home-turn-off-back-lights"
    # Entrance lights
    HOME_TURN_ON_ENTRANCE_LIGHTS = "home-turn-on-entrance-lights"
    HOME_TURN_OFF_ENTRANCE_LIGHTS = "home-turn-off-entrance-lights"
    # Garage lights
    HOME_TURN_ON_GARAGE_LIGHTS = "home-turn-on-garage-lights"
    HOME_TURN_OFF_GARAGE_LIGHTS = "home-turn-off-garage-lights"
    # Christmas lights
    HOME_TURN_ON_CHRISTMAS_LIGHTS = "home-turn-on-christmas-lights"
    HOME_TURN_OFF_CHRISTMAS_LIGHTS = "home-turn-off-christmas-lights"

    # Milencinos

    # Irrigation
    ME_OPEN_FRONT_IRRIGATION_V1 = "milencinos-open-front-irrigation-v1"
    ME_CLOSE_FRONT_IRRIGATION_V1 = "milencinos-close-front-irrigation-v1"
    ME_OPEN_FRONT_IRRIGATION_V2 = "milencinos-open-front-irrigation-v2"
    ME_CLOSE_FRONT_IRRIGATION_V2 = "milencinos-close-front-irrigation-v2"
    ME_OPEN_FRONT_IRRIGATION_V3 = "milencinos-open-front-irrigation-v3"
    ME_CLOSE_FRONT_IRRIGATION_V3 = "milencinos-close-front-irrigation-v3"
    ME_OPEN_FRONT_IRRIGATION_V4 = "milencinos-open-front-irrigation-v4"
    ME_CLOSE_FRONT_IRRIGATION_V4 = "milencinos-close-front-irrigation-v4"
    ME_OPEN_FRONT_IRRIGATION_V5 = "milencinos-open-front-irrigation-v5"
    ME_CLOSE_FRONT_IRRIGATION_V5 = "milencinos-close-front-irrigation-v5"
    ME_OPEN_FRONT_IRRIGATION_V6 = "milencinos-open-front-irrigation-v6"
    ME_CLOSE_FRONT_IRRIGATION_V6 = "milencinos-close-front-irrigation-v6"

    ME_OPEN_BACK_IRRIGATION_V1 = "milencinos-open-back-irrigation-v1"
    ME_CLOSE_BACK_IRRIGATION_V1 = "milencinos-close-back-irrigation-v1"
    ME_OPEN_BACK_IRRIGATION_V2 = "milencinos-open-back-irrigation-v2"
    ME_CLOSE_BACK_IRRIGATION_V2 = "milencinos-close-back-irrigation-v2"
    ME_OPEN_BACK_IRRIGATION_V3 = "milencinos-open-back-irrigation-v3"
    ME_CLOSE_BACK_IRRIGATION_V3 = "milencinos-close-back-irrigation-v3"
    ME_OPEN_BACK_IRRIGATION_V4 = "milencinos-open-back-irrigation-v4"
    ME_CLOSE_BACK_IRRIGATION_V4 = "milencinos-close-back-irrigation-v4"
    ME_OPEN_BACK_IRRIGATION_V5 = "milencinos-open-back-irrigation-v5"
    ME_CLOSE_BACK_IRRIGATION_V5 = "milencinos-close-back-irrigation-v5"
    ME_OPEN_BACK_IRRIGATION_V6 = "milencinos-open-back-irrigation-v6"
    ME_CLOSE_BACK_IRRIGATION_V6 = "milencinos-close-back-irrigation-v6"

    # Maps the endpoint to the task name.
    ENDPOINT_TASK_MAP = {
        # Home
        # Irrigation
        "/home/irrigation?state=open": HOME_OPEN_IRRIGATION,
        "/home/irrigation?state=closed": HOME_CLOSE_IRRIGATION,
        # Pool Pump
        "/home/poolPump?state=on": HOME_TURN_ON_POOL_PUMP,
        "/home/poolPump?state=off": HOME_TURN_OFF_POOL_PUMP,
        # Pool Pump
        "/home/poolWater?state=open": HOME_OPEN_POOL_WATER,
        "/home/poolWater?state=closed": HOME_CLOSE_POOL_WATER,
        # Bar Pump
        "/home/barPump?state=on": HOME_TURN_ON_BAR_PUMP,
        "/home/barPump?state=off": HOME_TURN_OFF_BAR_PUMP,
        # Front Lights
        "/home/frontLights?state=on": HOME_TURN_ON_FRONT_LIGHTS,
        "/home/frontLights?state=off": HOME_TURN_OFF_FRONT_LIGHTS,
        # Front Spot Lights
        "/home/frontSpotLights?state=on": HOME_TURN_ON_FRONT_SPOT_LIGHTS,
        "/home/frontSpotLights?state=off": HOME_TURN_OFF_FRONT_SPOT_LIGHTS,
        # Back Lights
        "/home/backLights?state=on": HOME_TURN_ON_BACK_LIGHTS,
        "/home/backLights?state=off": HOME_TURN_OFF_BACK_LIGHTS,
        # Entrance Lights
        "/home/entranceLights?state=on": HOME_TURN_ON_ENTRANCE_LIGHTS,
        "/home/entranceLights?state=off": HOME_TURN_OFF_ENTRANCE_LIGHTS,
        # Garage Lights
        "/home/garageLights?state=on": HOME_TURN_ON_GARAGE_LIGHTS,
        "/home/garageLights?state=off": HOME_TURN_OFF_GARAGE_LIGHTS,
        # Christmas Lights
        "/home/christmasLights?state=on": HOME_TURN_ON_CHRISTMAS_LIGHTS,
        "/home/christmasLights?state=off": HOME_TURN_OFF_CHRISTMAS_LIGHTS,
        # Milencinos
        # Irrigation
        "/milencinos/irrigation/front/v1?state=open": ME_OPEN_FRONT_IRRIGATION_V1,
        "/milencinos/irrigation/front/v1?state=closed": ME_CLOSE_FRONT_IRRIGATION_V1,
        "/milencinos/irrigation/front/v2?state=open": ME_OPEN_FRONT_IRRIGATION_V2,
        "/milencinos/irrigation/front/v2?state=closed": ME_CLOSE_FRONT_IRRIGATION_V2,
        "/milencinos/irrigation/front/v3?state=open": ME_OPEN_FRONT_IRRIGATION_V3,
        "/milencinos/irrigation/front/v3?state=closed": ME_CLOSE_FRONT_IRRIGATION_V3,
        "/milencinos/irrigation/front/v4?state=open": ME_OPEN_FRONT_IRRIGATION_V4,
        "/milencinos/irrigation/front/v4?state=closed": ME_CLOSE_FRONT_IRRIGATION_V4,
        "/milencinos/irrigation/front/v5?state=open": ME_OPEN_FRONT_IRRIGATION_V5,
        "/milencinos/irrigation/front/v5?state=closed": ME_CLOSE_FRONT_IRRIGATION_V5,
        "/milencinos/irrigation/front/v6?state=open": ME_OPEN_FRONT_IRRIGATION_V6,
        "/milencinos/irrigation/front/v6?state=closed": ME_CLOSE_FRONT_IRRIGATION_V6,
        "/milencinos/irrigation/back/v1?state=open": ME_OPEN_BACK_IRRIGATION_V1,
        "/milencinos/irrigation/back/v1?state=closed": ME_CLOSE_BACK_IRRIGATION_V1,
        "/milencinos/irrigation/back/v2?state=open": ME_OPEN_BACK_IRRIGATION_V2,
        "/milencinos/irrigation/back/v2?state=closed": ME_CLOSE_BACK_IRRIGATION_V2,
        "/milencinos/irrigation/back/v3?state=open": ME_OPEN_BACK_IRRIGATION_V3,
        "/milencinos/irrigation/back/v3?state=closed": ME_CLOSE_BACK_IRRIGATION_V3,
        "/milencinos/irrigation/back/v4?state=open": ME_OPEN_BACK_IRRIGATION_V4,
        "/milencinos/irrigation/back/v4?state=closed": ME_CLOSE_BACK_IRRIGATION_V4,
        "/milencinos/irrigation/back/v5?state=open": ME_OPEN_BACK_IRRIGATION_V5,
        "/milencinos/irrigation/back/v5?state=closed": ME_CLOSE_BACK_IRRIGATION_V5,
        "/milencinos/irrigation/back/v6?state=open": ME_OPEN_BACK_IRRIGATION_V6,
        "/milencinos/irrigation/back/v6?state=closed": ME_CLOSE_BACK_IRRIGATION_V6,
    }

    # Maps the task to the endpoint that task executes.
    TASK_MAP = {
        # AC Master
        TURN_ON_COOLING_MASTER: "ac/master?state=cooling",
        TURN_ON_HEAT_MASTER: "ac/master?state=heating",
        TURN_OFF_AC_MASTER: "ac/master?state=off",
        # AC JF
        TURN_ON_COOLING_JF: "ac/jf?state=cooling",
        TURN_ON_HEAT_JF: "ac/jf?state=heating",
        TURN_OFF_AC_JF: "ac/jf?state=off",
        # Smart lock
        OPEN_SMART_LOCK: "smartLock?state=open",
        CLOSE_SMART_LOCK: "smartLock?state=closed",
        # Alarm
        ARM_ALARM: "alarm?state=armed",
        DISARM_ALARM: "alarm?state=disarmed",
        # Home
        # Irrigation
        HOME_OPEN_IRRIGATION: "home/irrigation?state=open",
        HOME_CLOSE_IRRIGATION: "home/irrigation?state=closed",
        # Pool Pump
        HOME_TURN_ON_POOL_PUMP: "home/poolPump?state=on",
        HOME_TURN_OFF_POOL_PUMP: "home/poolPump?state=off",
        # Pool water
        HOME_OPEN_POOL_WATER: "home/poolWater?state=open",
        HOME_CLOSE_POOL_WATER: "home/poolWater?state=closed",
        # Bar Pump
        HOME_TURN_ON_BAR_PUMP: "home/barPump?state=on",
        HOME_TURN_OFF_BAR_PUMP: "home/barPump?state=off",
        # Front lights
        HOME_TURN_ON_FRONT_LIGHTS: "home/frontLights?state=on",
        HOME_TURN_OFF_FRONT_LIGHTS: "home/frontLights?state=off",
        # Front spot lights
        HOME_TURN_ON_FRONT_SPOT_LIGHTS: "home/frontSpotLights?state=on",
        HOME_TURN_OFF_FRONT_SPOT_LIGHTS: "home/frontSpotLights?state=off",
        # Back Main lights
        HOME_TURN_ON_BACK_LIGHTS: "home/backLights?state=on",
        HOME_TURN_OFF_BACK_LIGHTS: "home/backLights?state=off",
        # Entrance lights
        HOME_TURN_ON_ENTRANCE_LIGHTS: "home/entranceLights?state=on",
        HOME_TURN_OFF_ENTRANCE_LIGHTS: "home/entranceLights?state=off",
        # Garage lights
        HOME_TURN_ON_GARAGE_LIGHTS: "home/garageLights?state=on",
        HOME_TURN_OFF_GARAGE_LIGHTS: "home/garageLights?state=off",
        # Christmas lights
        HOME_TURN_ON_CHRISTMAS_LIGHTS: "home/christmasLights?state=on",
        HOME_TURN_OFF_CHRISTMAS_LIGHTS: "home/christmasLights?state=off",
        # Milencinos
        # Irrigation
        ME_OPEN_FRONT_IRRIGATION_V1: "milencinos/irrigation/front/v1?state=open",
        ME_CLOSE_FRONT_IRRIGATION_V1: "milencinos/irrigation/front/v1?state=closed",
        ME_OPEN_FRONT_IRRIGATION_V2: "milencinos/irrigation/front/v2?state=open",
        ME_CLOSE_FRONT_IRRIGATION_V2: "milencinos/irrigation/front/v2?state=closed",
        ME_OPEN_FRONT_IRRIGATION_V3: "milencinos/irrigation/front/v3?state=open",
        ME_CLOSE_FRONT_IRRIGATION_V3: "milencinos/irrigation/front/v3?state=closed",
        ME_OPEN_FRONT_IRRIGATION_V4: "milencinos/irrigation/front/v4?state=open",
        ME_CLOSE_FRONT_IRRIGATION_V4: "milencinos/irrigation/front/v4?state=closed",
        ME_OPEN_FRONT_IRRIGATION_V5: "milencinos/irrigation/front/v5?state=open",
        ME_CLOSE_FRONT_IRRIGATION_V5: "milencinos/irrigation/front/v5?state=closed",
        ME_OPEN_FRONT_IRRIGATION_V6: "milencinos/irrigation/front/v6?state=open",
        ME_CLOSE_FRONT_IRRIGATION_V6: "milencinos/irrigation/front/v6?state=closed",
        ME_OPEN_BACK_IRRIGATION_V1: "milencinos/irrigation/back/v1?state=open",
        ME_CLOSE_BACK_IRRIGATION_V1: "milencinos/irrigation/back/v1?state=closed",
        ME_OPEN_BACK_IRRIGATION_V2: "milencinos/irrigation/back/v2?state=open",
        ME_CLOSE_BACK_IRRIGATION_V2: "milencinos/irrigation/back/v2?state=closed",
        ME_OPEN_BACK_IRRIGATION_V3: "milencinos/irrigation/back/v3?state=open",
        ME_CLOSE_BACK_IRRIGATION_V3: "milencinos/irrigation/back/v3?state=closed",
        ME_OPEN_BACK_IRRIGATION_V4: "milencinos/irrigation/back/v4?state=open",
        ME_CLOSE_BACK_IRRIGATION_V4: "milencinos/irrigation/back/v4?state=closed",
        ME_OPEN_BACK_IRRIGATION_V5: "milencinos/irrigation/back/v5?state=open",
        ME_CLOSE_BACK_IRRIGATION_V5: "milencinos/irrigation/back/v5?state=closed",
        ME_OPEN_BACK_IRRIGATION_V6: "milencinos/irrigation/back/v6?state=open",
        ME_CLOSE_BACK_IRRIGATION_V6: "milencinos/irrigation/back/v6?state=closed",
    }

    # Maps the tasks to their counter tasks
    COUNTER_TASK_MAP = {
        # AC Master
        TURN_ON_COOLING_MASTER: TURN_OFF_AC_MASTER,
        TURN_ON_HEAT_MASTER: TURN_OFF_AC_MASTER,
        # AC JF
        TURN_ON_COOLING_JF: TURN_OFF_AC_JF,
        TURN_ON_HEAT_JF: TURN_OFF_AC_JF,
        # Pool water
        HOME_OPEN_POOL_WATER: HOME_CLOSE_POOL_WATER,
        # Smart lock
        OPEN_SMART_LOCK: CLOSE_SMART_LOCK,
        # Alarm
        ARM_ALARM: DISARM_ALARM,
        # Home
        # Irrigation
        HOME_OPEN_IRRIGATION: HOME_CLOSE_IRRIGATION,
        # Pool Pump
        HOME_TURN_ON_POOL_PUMP: HOME_TURN_OFF_POOL_PUMP,
        # Bar Pump
        HOME_TURN_ON_BAR_PUMP: HOME_TURN_OFF_BAR_PUMP,
        # Front lights
        HOME_TURN_ON_FRONT_LIGHTS: HOME_TURN_OFF_FRONT_LIGHTS,
        # Front spot lights
        HOME_TURN_ON_FRONT_SPOT_LIGHTS: HOME_TURN_OFF_FRONT_SPOT_LIGHTS,
        # Back Main lights
        HOME_TURN_ON_BACK_LIGHTS: HOME_TURN_OFF_BACK_LIGHTS,
        # Entrance lights
        HOME_TURN_ON_ENTRANCE_LIGHTS: HOME_TURN_OFF_ENTRANCE_LIGHTS,
        # Garage lights
        HOME_TURN_ON_GARAGE_LIGHTS: HOME_TURN_OFF_GARAGE_LIGHTS,
        # Christmas lights
        HOME_TURN_ON_CHRISTMAS_LIGHTS: HOME_TURN_OFF_CHRISTMAS_LIGHTS,
        # Milencinos
        # Irrigation
        ME_OPEN_FRONT_IRRIGATION_V1: ME_CLOSE_FRONT_IRRIGATION_V1,
        ME_OPEN_FRONT_IRRIGATION_V2: ME_CLOSE_FRONT_IRRIGATION_V2,
        ME_OPEN_FRONT_IRRIGATION_V3: ME_CLOSE_FRONT_IRRIGATION_V3,
        ME_OPEN_FRONT_IRRIGATION_V4: ME_CLOSE_FRONT_IRRIGATION_V4,
        ME_OPEN_FRONT_IRRIGATION_V5: ME_CLOSE_FRONT_IRRIGATION_V5,
        ME_OPEN_FRONT_IRRIGATION_V6: ME_CLOSE_FRONT_IRRIGATION_V6,
        ME_OPEN_BACK_IRRIGATION_V1: ME_CLOSE_BACK_IRRIGATION_V1,
        ME_OPEN_BACK_IRRIGATION_V2: ME_CLOSE_BACK_IRRIGATION_V2,
        ME_OPEN_BACK_IRRIGATION_V3: ME_CLOSE_BACK_IRRIGATION_V3,
        ME_OPEN_BACK_IRRIGATION_V4: ME_CLOSE_BACK_IRRIGATION_V4,
        ME_OPEN_BACK_IRRIGATION_V5: ME_CLOSE_BACK_IRRIGATION_V5,
        ME_OPEN_BACK_IRRIGATION_V6: ME_CLOSE_BACK_IRRIGATION_V6,
    }

    @classmethod
    def convert_json_to_redis(cls, json_object: dict[str, Any]) -> dict[str, Any]:
        """
        Converts a json object to redis object by cleaning its fields.
        """
        redis_object = {}
        for key, value in json_object.items():
            redis_value = cls.convert_field_to_redis(key, value)
            if value is not None:
                redis_object[key] = redis_value
        return redis_object

    @classmethod
    def convert_field_to_redis(cls, key: str, value: Any) -> Any:  # pylint:disable=inconsistent-return-statements
        """
        Converts a field into a supported field in redis
        """
        if key not in cls.SCHEMA:
            return None

        key_type = cls.SCHEMA[key]
        if key_type == "string":
            return value
        if key_type == "bool":
            if value:
                return "True"
            return "False"
        if key_type == "object":
            return json.dumps(value)

    @classmethod
    def convert_redis_to_json(cls, redis_object):
        """
        Converts a redis object to json object by cleaning its fields.
        """
        json_object = {}
        for key, value in redis_object.items():
            key = key.decode("utf-8")
            json_value = cls.convert_field_to_json(key, value)
            if json_value is not None:
                json_object[key] = json_value
        return json_object

    @classmethod
    def convert_field_to_json(cls, key, value) -> Any:  # pylint:disable=inconsistent-return-statements
        """
        Converts a field from a supported redis field to json
        """
        if key not in cls.SCHEMA:
            return None

        key_type = cls.SCHEMA[key]
        if key_type == "string":
            return value.decode("utf-8")
        if key_type == "bool":
            if value == b"True":
                return True
            return False
        if key_type == "object":
            return json.loads(value.decode("utf-8"))

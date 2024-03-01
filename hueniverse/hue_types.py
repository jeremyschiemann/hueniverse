from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Any



class DiscoveredBridge(BaseModel):
    id: str
    internalipaddress: str
    port: int

class AppKeyResponse(BaseModel):
    username: str
    clientkey: str


class ResourceType(str, Enum):
    DEVICE = 'device'
    BRIDGE_HOME = 'bridge_home'
    ROOM = 'room'
    ZONE = 'zone'
    LIGHT = 'light'
    BUTTON = 'button'
    RELATIVE_ROTARY = 'relative_rotary'
    TEMPERATURE = 'temperature'
    LIGHT_LEVEL = 'light_level'
    MOTION = 'motion'
    CAMERA_MOTION = 'camera_motion'
    ENTERTAINMENT = 'entertainment'
    CONTACT = 'contact'
    TAMPER = 'tamper'
    GROUPED_LIGHT = 'grouped_light'
    DEVICE_POWER = 'device_power'
    ZIGBEE_BRIDGE_CONNECTIVITY = 'zigbee_bridge_connectivity'
    ZIGBEE_CONNECTIVITY = 'zigbee_connectivity'
    ZGP_CONNECTIVITY = 'zgp_connectivity'
    BRIDGE = 'bridge'
    ZIGBEE_DEVICE_DISCOVERY = 'zigbee_device_discovery'
    HOMEKIT = 'homekit'
    MATTER = 'matter'
    MATTER_FABRIC = 'matter_fabric'
    SCENE = 'scene'
    ENTERTAINMENT_CONFIGURATION = 'entertainment_configuration'
    PUBLIC_IMAGE = 'public_image'
    AUTH_V1 = 'auth_v1'
    BEHAVIOR_SCRIPT = 'behavior_script'
    BEHAVIOR_INSTANCE = 'behavior_instance'
    GEOFENCE = 'geofence'
    GEOFENCE_CLIENT = 'geofence_client'
    GEOLOCATION = 'geolocation'
    SMART_SCENE = 'smart_scene'

class ArcheType(str, Enum):
    UNKNOWN_ARCHETYPE = 'unknown_archetype'
    CLASSIC_BULB = 'classic_bulb'
    SULTAN_BULB = 'sultan_bulb'
    FLOOD_BULB = 'flood_bulb'
    SPOT_BULB = 'spot_bulb'
    CANDLE_BULB = 'candle_bulb'
    LUSTER_BULB = 'luster_bulb'
    PENDANT_ROUND = 'pendant_round'
    PENDANT_LONG = 'pendant_long'
    CEILING_ROUND = 'ceiling_round'
    CEILING_SQUARE = 'ceiling_square'
    FLOOR_SHADE = 'floor_shade'
    FLOOR_LANTERN = 'floor_lantern'
    TABLE_SHADE = 'table_shade'
    RECESSED_CEILING = 'recessed_ceiling'
    RECESSED_FLOOR = 'recessed_floor'
    SINGLE_SPOT = 'single_spot'
    DOUBLE_SPOT = 'double_spot'
    TABLE_WASH = 'table_wash'
    WALL_LANTERN = 'wall_lantern'
    WALL_SHADE = 'wall_shade'
    FLEXIBLE_LAMP = 'flexible_lamp'
    GROUND_SPOT = 'ground_spot'
    WALL_SPOT = 'wall_spot'
    PLUG = 'plug'
    HUE_GO = 'hue_go'
    HUE_LIGHTSTRIP = 'hue_lightstrip'
    HUE_IRIS = 'hue_iris'
    HUE_BLOOM = 'hue_bloom'
    BOLLARD = 'bollard'
    WALL_WASHER = 'wall_washer'
    HUE_PLAY = 'hue_play'
    VINTAGE_BULB = 'vintage_bulb'
    VINTAGE_CANDLE_BULB = 'vintage_candle_bulb'
    ELLIPSE_BULB = 'ellipse_bulb'
    TRIANGLE_BULB = 'triangle_bulb'
    SMALL_GLOBE_BULB = 'small_globe_bulb'
    LARGE_GLOBE_BULB = 'large_globe_bulb'
    EDISON_BULB = 'edison_bulb'
    CHRISTMAS_TREE = 'christmas_tree'
    STRING_LIGHT = 'string_light'
    HUE_CENTRIS = 'hue_centris'
    HUE_LIGHTSTRIP_TV = 'hue_lightstrip_tv'
    HUE_LIGHTSTRIP_PC = 'hue_lightstrip_pc'
    HUE_TUBE = 'hue_tube'
    HUE_SIGNE = 'hue_signe'
    PENDANT_SPOT = 'pendant_spot'
    CEILING_HORIZONTAL = 'ceiling_horizontal'
    CEILING_TUBE = 'ceiling_tube'

class Status(str, Enum):
    SET = 'set'
    CHANGING = 'changing'

class ProductData(BaseModel):
    model_id: str
    manufacturer_name: str
    product_name: str
    product_archetype: ArcheType
    certified: bool
    software_version: str
    hardware_platform_type: str

class Metadata(BaseModel):
    name: str
    archetype: ArcheType

class Usertest(BaseModel):
    status: Status
    usertest: bool

class ResourceIdentifier(BaseModel):
    rid: str
    rtype: ResourceType

class LightMetadata(Metadata):
    function: str

class On(BaseModel):
    on: bool

class Dimming(BaseModel):
    brightness: float
    min_dim_level: float

class MirekSchema(BaseModel):
    mirek_minimum: int
    mirek_maximum: int

class ColorTemperature(BaseModel):
    mirek: int | None
    mirek_valid: bool
    mirek_schema: MirekSchema

class XYColor(BaseModel):
    x: float
    y: float

class Gamut(BaseModel):
    red: XYColor
    green: XYColor
    blue: XYColor

class GamutType(str, Enum):
    C = 'C'
    B = 'B'
    A = 'A'

class Color(BaseModel):
    xy: XYColor
    gamut: Gamut
    gamut_type: GamutType


class Resource(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )

    bridge: Any


class Light(Resource):
    type: ResourceType
    id: str
    id_v1: str
    owner: ResourceIdentifier
    metadata: LightMetadata
    on: On
    dimming: Dimming | None = None
    color_temperature: ColorTemperature | None = None
    color: Color | None = None


    async def _put_on(self):
        return await self.bridge.put_resource(
            resource_type=self.type,
            resource_identifier=self.id,
            data=self.model_dump(include={'on'})
        )

    async def turn_on(self):
        """Turn the light on."""
        self.on.on = True
        await self._put_on()

    async def turn_off(self):
        """Turn the light off."""
        self.on.on = False
        await self._put_on()

    async def toggle_on(self):
        """Toggle the light on and off."""
        self.on.on = not self.on.on
        await self._put_on()


    #dynamics: Dynamics
    #alert: Alert
    #signaling: Signaling
    #mode: Mode
    #gradient: Gradient
    #effects: Effects
    #timed_effects: TimedEffects
    #powerup: Powerup



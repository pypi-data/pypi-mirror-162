from .protocol import Symbol


class EuOverlay20Functions:
    pass


class EuOverlay20Data:
    RECYCLE_MENU_CONFIRM_1 = Symbol([0x2E44], [0x238DAC4], 0x18, "")

    RECYCLE_MENU_CONFIRM_2 = Symbol([0x2E5C], [0x238DADC], 0x18, "")

    RECYCLE_SUBMENU_1 = Symbol([0x2E74], [0x238DAF4], 0x18, "")

    RECYCLE_SUBMENU_2 = Symbol([0x2E8C], [0x238DB0C], 0x20, "")

    RECYCLE_MAIN_MENU_1 = Symbol([0x2EAC], [0x238DB2C], 0x28, "")

    RECYCLE_MAIN_MENU_2 = Symbol([0x2F48], [0x238DBC8], 0x20, "")

    RECYCLE_MAIN_MENU_3 = Symbol([0x2FB8], [0x238DC38], 0x18, "")


class EuOverlay20Section:
    name = "overlay20"
    description = "Controls the Recycle Shop."
    loadaddress = 0x238AC80
    length = 0x3000
    functions = EuOverlay20Functions
    data = EuOverlay20Data


class EuOverlay3Functions:
    pass


class EuOverlay3Data:
    pass


class EuOverlay3Section:
    name = "overlay3"
    description = "Controls the Friend Rescue submenu within the top menu."
    loadaddress = 0x233D200
    length = 0xA160
    functions = EuOverlay3Functions
    data = EuOverlay3Data


class EuOverlay8Functions:
    pass


class EuOverlay8Data:
    pass


class EuOverlay8Section:
    name = "overlay8"
    description = (
        "Controls the Send Demo Dungeon submenu within the top menu (under 'Other')."
    )
    loadaddress = 0x233D200
    length = 0x2620
    functions = EuOverlay8Functions
    data = EuOverlay8Data


class EuOverlay5Functions:
    pass


class EuOverlay5Data:
    pass


class EuOverlay5Section:
    name = "overlay5"
    description = "Controls the Trade Team submenu within the top menu."
    loadaddress = 0x233D200
    length = 0x3240
    functions = EuOverlay5Functions
    data = EuOverlay5Data


class EuOverlay17Functions:
    pass


class EuOverlay17Data:
    ASSEMBLY_MENU_CONFIRM = Symbol([0x1A44], [0x238C6C4], 0x18, "")

    ASSEMBLY_MAIN_MENU_1 = Symbol([0x1A5C], [0x238C6DC], 0x18, "")

    ASSEMBLY_MAIN_MENU_2 = Symbol([0x1A74], [0x238C6F4], 0x20, "")

    ASSEMBLY_SUBMENU_1 = Symbol([0x1A94], [0x238C714], 0x28, "")

    ASSEMBLY_SUBMENU_2 = Symbol([0x1ABC], [0x238C73C], 0x30, "")

    ASSEMBLY_SUBMENU_3 = Symbol([0x1AEC], [0x238C76C], 0x30, "")

    ASSEMBLY_SUBMENU_4 = Symbol([0x1B1C], [0x238C79C], 0x38, "")

    ASSEMBLY_SUBMENU_5 = Symbol([0x1B54], [0x238C7D4], 0x38, "")

    ASSEMBLY_SUBMENU_6 = Symbol([0x1B8C], [0x238C80C], 0x38, "")

    ASSEMBLY_SUBMENU_7 = Symbol([0x1BC4], [0x238C844], 0x40, "")


class EuOverlay17Section:
    name = "overlay17"
    description = "Controls the Chimecho Assembly."
    loadaddress = 0x238AC80
    length = 0x1CE0
    functions = EuOverlay17Functions
    data = EuOverlay17Data


class EuOverlay19Functions:
    pass


class EuOverlay19Data:
    BAR_MENU_CONFIRM_1 = Symbol([0x40BC], [0x238ED3C], 0x18, "")

    BAR_MENU_CONFIRM_2 = Symbol([0x40D4], [0x238ED54], 0x18, "")

    BAR_MAIN_MENU = Symbol([0x4104], [0x238ED84], 0x20, "")

    BAR_SUBMENU_1 = Symbol([0x4124], [0x238EDA4], 0x20, "")

    BAR_SUBMENU_2 = Symbol([0x4144], [0x238EDC4], 0x30, "")


class EuOverlay19Section:
    name = "overlay19"
    description = "Controls Spinda's Juice Bar."
    loadaddress = 0x238AC80
    length = 0x4220
    functions = EuOverlay19Functions
    data = EuOverlay19Data


class EuOverlay12Functions:
    pass


class EuOverlay12Data:
    pass


class EuOverlay12Section:
    name = "overlay12"
    description = "Unused; all zeroes."
    loadaddress = 0x238AC80
    length = 0x20
    functions = EuOverlay12Functions
    data = EuOverlay12Data


class EuOverlay2Functions:
    pass


class EuOverlay2Data:
    pass


class EuOverlay2Section:
    name = "overlay2"
    description = (
        "Controls the Nintendo WFC Settings interface, accessed from the top menu"
        " (Other > Nintendo WFC > Nintendo WFC Settings). Presumably contains code for"
        " Nintendo Wi-Fi setup."
    )
    loadaddress = 0x2329D40
    length = 0x2AFC0
    functions = EuOverlay2Functions
    data = EuOverlay2Data


class EuOverlay28Functions:
    pass


class EuOverlay28Data:
    pass


class EuOverlay28Section:
    name = "overlay28"
    description = "Controls the staff credits sequence."
    loadaddress = 0x238AC80
    length = 0xC60
    functions = EuOverlay28Functions
    data = EuOverlay28Data


class EuOverlay29Functions:
    DungeonAlloc = Symbol(
        [0x281C],
        [0x22DF39C],
        None,
        "Allocates a new dungeon struct.\n\nThis updates the master dungeon pointer and"
        " returns a copy of that pointer.\n\nreturn: pointer to a newly allocated"
        " dungeon struct",
    )

    GetDungeonPtrMaster = Symbol(
        [0x2840],
        [0x22DF3C0],
        None,
        "Returns the master dungeon pointer (a global, see"
        " DUNGEON_PTR_MASTER).\n\nreturn: pointer to a newly allocated dungeon struct",
    )

    DungeonZInit = Symbol(
        [0x2850],
        [0x22DF3D0],
        None,
        "Zero-initializes the dungeon struct pointed to by the master dungeon"
        " pointer.\n\nNo params.",
    )

    DungeonFree = Symbol(
        [0x2870],
        [0x22DF3F0],
        None,
        "Frees the dungeons struct pointer to by the master dungeon pointer, and"
        " nullifies the pointer.\n\nNo params.",
    )

    RunDungeon = Symbol(
        [0x2CF8],
        [0x22DF878],
        None,
        "Called at the start of a dungeon. Initializes the dungeon struct from"
        " specified dungeon data. Includes a loop that does not break until the dungeon"
        " is cleared, and another one inside it that runs until the current floor"
        " ends.\n\nr0: Pointer to the struct containing info used to initialize the"
        " dungeon. See type dungeon_init for details.\nr1: Pointer to the dungeon data"
        " struct that will be used during the dungeon.",
    )

    EntityIsValid = Symbol(
        [
            0x4114,
            0x57DC,
            0x5DC7,
            0x7118,
            0x75E8,
            0xD424,
            0x10438,
            0x10BF0,
            0x12178,
            0x135D4,
            0x143C4,
            0x190C8,
            0x1A0E0,
            0x1B19C,
            0x20818,
            0x22338,
            0x23F90,
            0x268E4,
            0x28664,
            0x29438,
            0x29AB0,
            0x2BDA4,
            0x2CE68,
            0x327E4,
            0x32EFC,
            0x34EF0,
            0x35794,
            0x38FF8,
            0x3CC14,
            0x3CD2C,
            0x3DE6C,
            0x3F074,
            0x40AB0,
            0x42CC0,
            0x43458,
            0x43AE4,
            0x44064,
            0x4464C,
            0x49508,
            0x4BEF8,
            0x4E2C4,
            0x503F0,
            0x52110,
            0x52700,
            0x57E6C,
            0x58F98,
            0x5BCF8,
            0x68B5C,
            0x69704,
            0x6BC24,
            0x6D8FC,
            0x71E50,
            0x72CA0,
        ],
        [
            0x22E0C94,
            0x22E235C,
            0x22E2947,
            0x22E3C98,
            0x22E4168,
            0x22E9FA4,
            0x22ECFB8,
            0x22ED770,
            0x22EECF8,
            0x22F0154,
            0x22F0F44,
            0x22F5C48,
            0x22F6C60,
            0x22F7D1C,
            0x22FD398,
            0x22FEEB8,
            0x2300B10,
            0x2303464,
            0x23051E4,
            0x2305FB8,
            0x2306630,
            0x2308924,
            0x23099E8,
            0x230F364,
            0x230FA7C,
            0x2311A70,
            0x2312314,
            0x2315B78,
            0x2319794,
            0x23198AC,
            0x231A9EC,
            0x231BBF4,
            0x231D630,
            0x231F840,
            0x231FFD8,
            0x2320664,
            0x2320BE4,
            0x23211CC,
            0x2326088,
            0x2328A78,
            0x232AE44,
            0x232CF70,
            0x232EC90,
            0x232F280,
            0x23349EC,
            0x2335B18,
            0x2338878,
            0x23456DC,
            0x2346284,
            0x23487A4,
            0x234A47C,
            0x234E9D0,
            0x234F820,
        ],
        None,
        "Checks if an entity pointer points to a valid entity (not entity type 0, which"
        " represents no entity).\n\nr0: entity pointer\nreturn: bool",
    )

    GetFloorType = Symbol(
        [0x4170],
        [0x22E0CF0],
        None,
        "Get the current floor type.\n\nFloor types:\n  0 appears to mean the current"
        " floor is 'normal'\n  1 appears to mean the current floor is a fixed floor\n "
        " 2 means the current floor has a rescue point\n\nreturn: floor type",
    )

    TryForcedLoss = Symbol(
        [0x43E0],
        [0x22E0F60],
        None,
        "Attempts to trigger a forced loss of the type specified in"
        " dungeon::forced_loss_reason.\n\nr0: if true, the function will not check for"
        " the end of the floor condition and will skip other (unknown) actions in case"
        " of forced loss.\nreturn: true if the forced loss happens, false otherwise",
    )

    FixedRoomIsSubstituteRoom = Symbol(
        [0x468C],
        [0x22E120C],
        None,
        "Checks if the current fixed room is the 'substitute room' (ID"
        " 0x6E).\n\nreturn: bool",
    )

    StoryRestrictionsEnabled = Symbol(
        [0x46E8],
        [0x22E1268],
        None,
        "Returns true if certain special restrictions are enabled.\n\nIf true, you will"
        " get kicked out of the dungeon if a team member that passes the"
        " arm9::JoinedAtRangeCheck2 check faints.\n\nreturn: !dungeon::nonstory_flag ||"
        " dungeon::hidden_land_flag",
    )

    FadeToBlack = Symbol(
        [0x4728],
        [0x22E12A8],
        None,
        "Fades the screen to black across several frames.\n\nNo params.",
    )

    GetTileAtEntity = Symbol(
        [0x53E8],
        [0x22E1F68],
        None,
        "Returns a pointer to the tile where an entity is located.\n\nr0: pointer to"
        " entity\nreturns: pointer to tile",
    )

    CanTargetEntity = Symbol(
        [0x65D0],
        [0x22E3150],
        None,
        "Checks if a monster can target another entity when controlled by the AI.\nMore"
        " specifically, it checks if the target is invisible, if the user can see"
        " invisible monsters, if the user is blinded and if the target position is in"
        " sight from the position of the user (this last check is done by calling"
        " IsPositionInSight with the user's and the target's position).\n\nr0: User"
        " entity pointer\nr1: Target entity pointer\nreturn: True if the user can"
        " target the target",
    )

    CanTargetPosition = Symbol(
        [0x6714],
        [0x22E3294],
        None,
        "Checks if a monster can target a position. This function just calls"
        " IsPositionInSight using the position of the user as the origin.\n\nr0: Entity"
        " pointer\nr1: Target position\nreturn: True if the specified monster can"
        " target the target position, false otherwise.",
    )

    SubstitutePlaceholderStringTags = Symbol(
        [0x6898],
        [0x22E3418],
        None,
        "Replaces instances of a given placeholder tag by the string representation of"
        " the given entity.\n\nFrom the eos-move-effects docs (which are somewhat"
        " nebulous): 'Replaces the string at StringID [r0] by the string representation"
        " of the target [r1] (aka its name). Any message with the string manipulator"
        " '[string:StringID]' will use that string'.\n\nThe game uses various"
        " placeholder tags in its strings, which you can read about here:"
        " https://textbox.skytemple.org/.\n\nr0: string ID (unclear what this"
        " means)\nr1: entity pointer\nr2: ?",
    )

    UpdateMapSurveyorFlag = Symbol(
        [0x6BDC],
        [0x22E375C],
        None,
        "Sets the Map Surveyor flag in the dungeon struct to true if a team member has"
        " Map Surveyor, sets it to false otherwise.\n\nThis function has two variants:"
        " in the EU ROM, it will return true if the flag was changed. The NA version"
        " will return the new value of the flag instead.\n\nreturn: bool",
    )

    ItemIsActive = Symbol(
        [
            0x713C,
            0x12148,
            0x197D0,
            0x23744,
            0x26578,
            0x2BDC8,
            0x2E8D0,
            0x3246C,
            0x33704,
            0x34F14,
            0x35AD8,
            0x3901C,
            0x6BBD0,
        ],
        [
            0x22E3CBC,
            0x22EECC8,
            0x22F6350,
            0x23002C4,
            0x23030F8,
            0x2308948,
            0x230B450,
            0x230EFEC,
            0x2310284,
            0x2311A94,
            0x2312658,
            0x2315B9C,
            0x2348750,
        ],
        None,
        "Checks if a monster is holding a certain item that isn't disabled by"
        " Klutz.\n\nr0: entity pointer\nr1: item ID\nreturn: bool",
    )

    UpdateStatusIconFlags = Symbol(
        [0x78E4],
        [0x22E4464],
        None,
        "Sets a monster's status_icon_flags bitfield according to its current status"
        " effects. Does not affect a Sudowoodo in the 'permanent sleep' state"
        " (statuses::sleep == 0x7F).\n\nSome of the status effect in monster:statuses"
        " are used as an index to access an array, where every group of 8 bytes"
        " represents a bitmask. All masks are added in a bitwise OR and then stored in"
        " monster::status_icon.\n\nAlso sets icon flags for statuses::exposed,"
        " statuses::grudge, critical HP and lowered stats with explicit checks, and"
        " applies the effect of the Identifier Orb (see"
        " dungeon::identify_orb_flag).\n\nr0: entity pointer",
    )

    IsOnMonsterSpawnList = Symbol(
        [0xBB7C],
        [0x22E86FC],
        None,
        "Returns true if the specified monster is included in the floor's monster spawn"
        " list (the modified list after a maximum of 14 different species were chosen,"
        " not the raw list read from the mappa file).\n\nr0: Monster ID\nreturn: bool",
    )

    GetMonsterIdToSpawn = Symbol(
        [0xBBD0],
        [0x22E8750],
        None,
        "Get the id of the monster to be randomly spawned.\n\nr0: the spawn weight to"
        " use (0 for normal, 1 for monster house)\nreturn: monster ID",
    )

    GetMonsterLevelToSpawn = Symbol(
        [0xBC88],
        [0x22E8808],
        None,
        "Get the level of the monster to be spawned, given its id.\n\nr0: monster"
        " ID\nreturn: Level of the monster to be spawned, or 1 if the specified ID"
        " can't be found on the floor's spawn table.",
    )

    GetDirectionTowardsPosition = Symbol(
        [0xCE50],
        [0x22E99D0],
        None,
        "Gets the direction in which a monster should move to go from the origin"
        " position to the target position\n\nr0: Origin position\nr1: Target"
        " position\nreturn: Direction in which to move to reach the target position"
        " from the origin position",
    )

    GetChebyshevDistance = Symbol(
        [0xCEBC],
        [0x22E9A3C],
        None,
        "Returns the Chebyshev distance between two positions. Calculated as"
        " max(abs(x0-x1), abs(y0-y1)).\n\nr0: Position A\nr1: Position B\nreturn:"
        " Chebyshev Distance between position A and position B",
    )

    IsPositionInSight = Symbol(
        [0xCFD4],
        [0x22E9B54],
        None,
        "Checks if a given target position is in sight from a given origin"
        " position.\nThere's multiple factors that affect this check, but generally,"
        " it's true if both positions are in the same room or within 2 tiles of each"
        " other.\n\nr0: Origin position\nr1: Target position\nr2: True to assume the"
        " entity standing on the origin position has the dropeye status\nreturn: True"
        " if the target position is in sight from the origin position",
    )

    GetLeader = Symbol(
        [0xD3B0],
        [0x22E9F30],
        None,
        "Gets the pointer to the entity that is currently leading the team, or null if"
        " none of the first 4 entities is a valid monster with its is_team_leader flag"
        " set. It also sets LEADER_PTR to the result before returning it.\n\nreturn:"
        " Pointer to the current leader of the team or null if there's no valid"
        " leader.",
    )

    TickStatusTurnCounter = Symbol(
        [0xD874],
        [0x22EA3F4],
        None,
        "Ticks down a turn counter for a status condition. If the counter equals 0x7F,"
        " it will not be decreased.\n\nr0: pointer to the status turn counter\nreturn:"
        " new counter value",
    )

    AdvanceFrame = Symbol(
        [0xDE10],
        [0x22EA990],
        None,
        "Advances one frame. Does not return until the next frame starts.\n\nr0: ? -"
        " Unused by the function",
    )

    GenerateDungeonRngSeed = Symbol(
        [0xE7B0],
        [0x22EB330],
        None,
        "Generates a seed with which to initialize the dungeon PRNG.\n\nThe seed is"
        " calculated by starting with a different seed, the 'preseed' x0 (defaults to"
        " 1, but can be set by other functions). The preseed is iterated twice with the"
        " same recurrence relation used in the primary LCG to generate two pseudorandom"
        " 32-bit numbers x1 and x2. The output seed is then computed as\n  seed = (x1 &"
        " 0xFF0000) | (x2 >> 0x10) | 1\nThe value x1 is then saved as the new"
        " preseed.\n\nThis method of seeding the dungeon PRNG appears to be used only"
        " sometimes, depending on certain flags in the data for a given"
        " dungeon.\n\nreturn: RNG seed",
    )

    GetDungeonRngPreseed = Symbol(
        [0xE7FC],
        [0x22EB37C],
        None,
        "Gets the current preseed stored in the global dungeon PRNG state. See"
        " GenerateDungeonRngSeed for more information.\n\nreturn: current dungeon RNG"
        " preseed",
    )

    SetDungeonRngPreseed = Symbol(
        [0xE80C],
        [0x22EB38C],
        None,
        "Sets the preseed in the global dungeon PRNG state. See GenerateDungeonRngSeed"
        " for more information.\n\nr0: preseed",
    )

    InitDungeonRng = Symbol(
        [0xE81C],
        [0x22EB39C],
        None,
        "Initialize (or reinitialize) the dungeon PRNG with a given seed. The primary"
        " LCG and the five secondary LCGs are initialized jointly, and with the same"
        " seed.\n\nr0: seed",
    )

    DungeonRand16Bit = Symbol(
        [0xE850],
        [0x22EB3D0],
        None,
        "Computes a pseudorandom 16-bit integer using the dungeon PRNG.\n\nNote that"
        " the dungeon PRNG is only used in dungeon mode (as evidenced by these"
        " functions being in overlay 29). The game uses another lower-quality PRNG (see"
        " arm9.yml) for other needs.\n\nRandom numbers are generated with a linear"
        " congruential generator (LCG). The game actually maintains 6 separate"
        " sequences that can be used for generation: a primary LCG and 5 secondary"
        " LCGs. The generator used depends on parameters set on the global PRNG"
        " state.\n\nAll dungeon LCGs have a modulus of 2^32 and a multiplier of"
        " 1566083941 (see DUNGEON_PRNG_LCG_MULTIPLIER). The primary LCG uses an"
        " increment of 1, while the secondary LCGs use an increment of 2531011 (see"
        " DUNGEON_PRNG_LCG_INCREMENT_SECONDARY). So, for example, the primary LCG uses"
        " the recurrence relation:\n  x = (1566083941*x_prev + 1) % 2^32\n\nSince the"
        " dungeon LCGs generate 32-bit integers rather than 16-bit, the primary LCG"
        " yields 16-bit values by taking the upper 16 bits of the computed 32-bit"
        " value. The secondary LCGs yield 16-bit values by taking the lower 16 bits of"
        " the computed 32-bit value.\n\nAll of the dungeon LCGs have a hard-coded"
        " default seed of 1, but in practice the seed is set with a call to"
        " InitDungeonRng during dungeon initialization.\n\nreturn: pseudorandom int on"
        " the interval [0, 65535]",
    )

    DungeonRandInt = Symbol(
        [0xE8C8],
        [0x22EB448],
        None,
        "Compute a pseudorandom integer under a given maximum value using the dungeon"
        " PRNG.\n\nr0: high\nreturn: pseudorandom integer on the interval [0, high"
        " - 1]",
    )

    DungeonRandRange = Symbol(
        [0xE8F0],
        [0x22EB470],
        None,
        "Compute a pseudorandom value between two integers using the dungeon"
        " PRNG.\n\nr0: x\nr1: y\nreturn: pseudorandom integer on the interval [min(x,"
        " y), max(x, y) - 1]",
    )

    DungeonRandOutcome = Symbol(
        [0xE950, 0xE980],
        [0x22EB4D0, 0x22EB500],
        None,
        "Returns the result of a possibly biased coin flip (a Bernoulli random"
        " variable) with some success probability p, using the dungeon PRNG.\n\nr0:"
        " success percentage (100*p)\nreturn: true with probability p, false with"
        " probability (1-p)",
    )

    CalcStatusDuration = Symbol(
        [0xE9B0],
        [0x22EB530],
        None,
        "Seems to calculate the duration of a volatile status on a monster.\n\nr0:"
        " entity pointer\nr1: pointer to a turn range (an array of two shorts {lower,"
        " higher})\nr2: flag for whether or not to factor in the Self Curer IQ skill"
        " and the Natural Cure ability\nreturn: number of turns for the status"
        " condition",
    )

    DungeonRngUnsetSecondary = Symbol(
        [0xEA64],
        [0x22EB5E4],
        None,
        "Sets the dungeon PRNG to use the primary LCG for subsequent random number"
        " generation, and also resets the secondary LCG index back to 0.\n\nSimilar to"
        " DungeonRngSetPrimary, but DungeonRngSetPrimary doesn't modify the secondary"
        " LCG index if it was already set to something other than 0.\n\nNo params.",
    )

    DungeonRngSetSecondary = Symbol(
        [0xEA7C],
        [0x22EB5FC],
        None,
        "Sets the dungeon PRNG to use one of the 5 secondary LCGs for subsequent random"
        " number generation.\n\nr0: secondary LCG index",
    )

    DungeonRngSetPrimary = Symbol(
        [0xEA94],
        [0x22EB614],
        None,
        "Sets the dungeon PRNG to use the primary LCG for subsequent random number"
        " generation.\n\nNo params.",
    )

    TrySwitchPlace = Symbol(
        [0xEFA8],
        [0x22EBB28],
        None,
        "The user entity attempts to switch places with the target entity (i.e. by the"
        " effect of the Switcher Orb). \n\nThe function checks for the Suction Cups"
        " ability for both the user and the target, and for the Mold Breaker ability on"
        " the user.\n\nr0: pointer to user entity\nr1: pointer to target entity",
    )

    ClearMonsterActionFields = Symbol(
        [0xF224],
        [0x22EBDA4],
        None,
        "Clears the fields related to AI in the monster's data struct, setting them all"
        " to 0.\nSpecifically, monster::action_id, monster::action_use_idx and"
        " monster::field_0x54 are cleared.\n\nr0: Pointer to the monster's action_id"
        " field (this field is probably contained in a struct)",
    )

    SetMonsterActionFields = Symbol(
        [0xF238],
        [0x22EBDB8],
        None,
        "Sets some the fields related to AI in the monster's data"
        " struct.\nSpecifically, monster::action_id, monster::action_use_idx and"
        " monster::field_0x54. The last 2 are always set to 0.\n\nr0: Pointer to the"
        " monster's action_id field (this field is probably contained in a struct)\nr1:"
        " Value to set monster::action_id to.",
    )

    SetActionPassTurnOrWalk = Symbol(
        [0xF24C],
        [0x22EBDCC],
        None,
        "Sets a monster's action to action::ACTION_PASS_TURN or action::ACTION_WALK,"
        " depending on the result of GetCanMoveFlag for the monster's ID.\n\nr0:"
        " Pointer to the monster's action_id field (this field is probably contained in"
        " a struct)\nr1: Monster ID",
    )

    SetActionRegularAttack = Symbol(
        [0xFA80],
        [0x22EC600],
        None,
        "Sets a monster's action to action::ACTION_REGULAR_ATTACK, with a specified"
        " direction.\n\nr0: Pointer to the monster's action_id field (this field is"
        " probably contained in a struct)\nr1: Direction in which to use the move. Gets"
        " stored in monster::direction.",
    )

    SetActionUseMoveAi = Symbol(
        [0xFAEC],
        [0x22EC66C],
        None,
        "Sets a monster's action to action::ACTION_USE_MOVE_AI, with a specified"
        " direction and move index.\n\nr0: Pointer to the monster's action_id field"
        " (this field is probably contained in a struct)\nr1: Index of the move to use"
        " (0-3). Gets stored in monster::action_use_idx.\nr2: Direction in which to use"
        " the move. Gets stored in monster::direction.",
    )

    RunFractionalTurn = Symbol(
        [0xFB38],
        [0x22EC6B8],
        None,
        "The main function which executes the actions that take place in a fractional"
        " turn. Called in a loop by RunDungeon while IsFloorOver returns false.\n\nr0:"
        " first loop flag (true when the function is first called during a floor)",
    )

    RunLeaderTurn = Symbol(
        [0x10138],
        [0x22ECCB8],
        None,
        "Handles the leader's turn. Includes a movement speed check that might cause it"
        " to return early if the leader isn't fast enough to act in this fractional"
        " turn. If that check (and some others) pass, the function does not return"
        " until the leader performs an action.\n\nr0: ?\nreturn: true if the leader has"
        " performed an action",
    )

    TrySpawnMonsterAndActivatePlusMinus = Symbol(
        [0x1050C],
        [0x22ED08C],
        None,
        "Called at the beginning of RunFractionalTurn. Executed only if"
        " FRACTIONAL_TURN_SEQUENCE[fractional_turn * 2] is not 0.\n\nFirst it calls"
        " TrySpawnMonsterAndTickSpawnCounter, then tries to activate the Plus and Minus"
        " abilities for both allies and enemies, and finally calls TryForcedLoss.\n\nNo"
        " params.",
    )

    IsFloorOver = Symbol(
        [0x10618],
        [0x22ED198],
        None,
        "Checks if the current floor should end, and updates dungeon::floor_loop_status"
        " if required.\nIf the player has been defeated, sets"
        " dungeon::floor_loop_status to"
        " floor_loop_status::FLOOR_LOOP_LEADER_FAINTED.\nIf dungeon::end_floor_flag is"
        " 1 or 2, sets dungeon::floor_loop_status to"
        " floor_loop_status::FLOOR_LOOP_NEXT_FLOOR.\n\nreturn: true if the current"
        " floor should end",
    )

    DecrementWindCounter = Symbol(
        [0x10978],
        [0x22ED4F8],
        None,
        "Decrements dungeon::wind_turns and displays a wind warning message if"
        " required.\n\nNo params.",
    )

    SetForcedLossReason = Symbol(
        [0x10E38],
        [0x22ED9B8],
        None,
        "Sets dungeon::forced_loss_reason to the specified value\n\nr0: Forced loss"
        " reason",
    )

    GetForcedLossReason = Symbol(
        [0x10E4C],
        [0x22ED9CC],
        None,
        "Returns dungeon::forced_loss_reason\n\nreturn: forced_loss_reason",
    )

    ResetDamageDesc = Symbol(
        [0x1AC50],
        [0x22F77D0],
        None,
        "Seems to zero some damage description struct, which is output by the damage"
        " calculation function.\n\nr0: damage description pointer",
    )

    GetSpriteIndex = Symbol(
        [0x1B1C0],
        [0x22F7D40],
        None,
        "Gets the sprite index of the specified monster on this floor\n\nr0: Monster"
        " ID\nreturn: Sprite index of the specified monster ID",
    )

    JoinedAtRangeCheck2Veneer = Symbol(
        [0x1B1E0],
        [0x22F7D60],
        None,
        "Likely a linker-generated veneer for arm9::JoinedAtRangeCheck2.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nNo"
        " params.",
    )

    FloorNumberIsEven = Symbol(
        [0x1B1EC],
        [0x22F7D6C],
        None,
        "Checks if the current dungeon floor number is even.\n\nHas a special check to"
        " return false for Labyrinth Cave B10F (the Gabite boss fight).\n\nreturn:"
        " bool",
    )

    GetKecleonIdToSpawnByFloor = Symbol(
        [0x1B224],
        [0x22F7DA4],
        None,
        "If the current floor number is even, returns female Kecleon's id (0x3D7),"
        " otherwise returns male Kecleon's id (0x17F).\n\nreturn: monster ID",
    )

    LoadMonsterSprite = Symbol(
        [0x1B48C],
        [0x22F800C],
        None,
        "Loads the sprite of the specified monster to use it in a dungeon.\n\nr0:"
        " Monster id\nr1: ?",
    )

    EuFaintCheck = Symbol(
        [0x1BD68],
        [0x22F88E8],
        None,
        "This function is exclusive to the EU ROM. Seems to perform a check to see if"
        " the monster who just fainted was a team member who should cause the minimap"
        " to be updated (or something like that, maybe related to the Map Surveyor IQ"
        " skill) and if it passes, updates the minimap.\nThe function ends by calling"
        " another 2 functions. In US ROMs, calls to EUFaintCheck are replaced by calls"
        " to those two functions. This seems to indicate that this function fixes some"
        " edge case glitch that can happen when a team member faints.\n\nr0: False if"
        " the fainted entity was a team member\nr1: True to set an unknown byte in the"
        " RAM to 1",
    )

    HandleFaint = Symbol(
        [0x1BDB8],
        [0x22F8938],
        None,
        "Handles a fainted pokémon (reviving does not count as fainting).\n\nr0:"
        " Fainted entity\nr1: Faint reason (move ID or greater than the max move id for"
        " other causes)\nr2: Entity responsible of the fainting",
    )

    UpdateAiTargetPos = Symbol(
        [0x1CFD0],
        [0x22F9B50],
        None,
        "Given a monster, updates its target_pos field based on its current position"
        " and the direction in which it plans to attack.\n\nr0: Entity pointer",
    )

    TryActivateSlowStart = Symbol(
        [0x1D0C8],
        [0x22F9C48],
        None,
        "Runs a check over all monsters on the field for the ability Slow Start, and"
        " lowers the speed of those who have it.\n\nNo params",
    )

    TryActivateArtificialWeatherAbilities = Symbol(
        [0x1D164],
        [0x22F9CE4],
        None,
        "Runs a check over all monsters on the field for abilities that affect the"
        " weather and changes the floor's weather accordingly.\n\nNo params",
    )

    DefenderAbilityIsActive = Symbol(
        [
            0x1D558,
            0x258B8,
            0x2E834,
            0x35A74,
            0x46C4C,
            0x4C520,
            0x4DE00,
            0x4FCC0,
            0x51CE0,
            0x568CC,
        ],
        [
            0x22FA0D8,
            0x2302438,
            0x230B3B4,
            0x23125F4,
            0x23237CC,
            0x23290A0,
            0x232A980,
            0x232C840,
            0x232E860,
            0x233344C,
        ],
        None,
        "Checks if a defender has an active ability that isn't disabled by an"
        " attacker's Mold Breaker.\n\nThere are two versions of this function, which"
        " share the same logic but have slightly different assembly. This is probably"
        " due to differences in compiler optimizations at different addresses.\n\nr0:"
        " attacker pointer\nr1: defender pointer\nr2: ability ID to check on the"
        " defender\nr3: flag for whether the attacker's ability is enabled\nreturn:"
        " bool",
    )

    IsMonster = Symbol(
        [
            0x1D5AC,
            0x2590C,
            0x2E888,
            0x33874,
            0x3C990,
            0x3E8B4,
            0x3F1F8,
            0x46CA0,
            0x714E0,
        ],
        [
            0x22FA12C,
            0x230248C,
            0x230B408,
            0x23103F4,
            0x2319510,
            0x231B434,
            0x231BD78,
            0x2323820,
            0x234E060,
        ],
        None,
        "Checks if an entity is a monster (entity type 1).\n\nr0: entity"
        " pointer\nreturn: bool",
    )

    TryActivateTruant = Symbol(
        [0x1D67C],
        [0x22FA1FC],
        None,
        "Checks if an entity has the ability Truant, and if so tries to apply the pause"
        " status to it.\n\nr0: pointer to entity",
    )

    RestorePpAllMovesSetFlags = Symbol(
        [0x1D900],
        [0x22FA480],
        None,
        "Restores PP for all moves, clears flags move::f_consume_2_pp,"
        " move::flags2_unk5 and move::flags2_unk7, and sets flag"
        " move::f_consume_pp.\nCalled when a monster is revived.\n\nr0: pointer to"
        " entity whose moves will be restored",
    )

    ShouldMonsterHeadToStairs = Symbol(
        [0x1E2BC],
        [0x22FAE3C],
        None,
        "Checks if a given monster should try to reach the stairs when controlled by"
        " the AI\n\nr0: Entity pointer\nreturn: True if the monster should try to reach"
        " the stairs, false otherwise",
    )

    MewSpawnCheck = Symbol(
        [0x1E47C],
        [0x22FAFFC],
        None,
        "If the monster id parameter is 0x97 (Mew), returns false if either"
        " dungeon::mew_cannot_spawn or the second parameter are true.\n\nCalled before"
        " spawning an enemy, appears to be checking if Mew can spawn on the current"
        " floor.\n\nr0: monster id\nr1: return false if the monster id is Mew\nreturn:"
        " bool",
    )

    ExclusiveItemEffectIsActive = Symbol(
        [
            0x1EB24,
            0x23DD4,
            0x2E8AC,
            0x337A0,
            0x34F44,
            0x386CC,
            0x3D688,
            0x3E75C,
            0x47800,
            0x568A8,
            0x6BC00,
            0x6C330,
        ],
        [
            0x22FB6A4,
            0x2300954,
            0x230B42C,
            0x2310320,
            0x2311AC4,
            0x231524C,
            0x231A208,
            0x231B2DC,
            0x2324380,
            0x2333428,
            0x2348780,
            0x2348EB0,
        ],
        None,
        "Checks if a monster is a team member under the effects of a certain exclusive"
        " item effect.\n\nr0: entity pointer\nr1: exclusive item effect ID\nreturn:"
        " bool",
    )

    GetTeamMemberWithIqSkill = Symbol(
        [0x1EE84],
        [0x22FBA04],
        None,
        "Returns an entity pointer to the first team member which has the specified iq"
        " skill.\n\nr0: iq skill id\nreturn: pointer to entity",
    )

    TeamMemberHasEnabledIqSkill = Symbol(
        [0x1EEF0],
        [0x22FBA70],
        None,
        "Returns true if any team member has the specified iq skill.\n\nr0: iq skill"
        " id\nreturn: bool",
    )

    TeamLeaderIqSkillIsEnabled = Symbol(
        [0x1EF0C],
        [0x22FBA8C],
        None,
        "Returns true the leader has the specified iq skill.\n\nr0: iq skill"
        " id\nreturn: bool",
    )

    HasLowHealth = Symbol(
        [0x1F49C],
        [0x22FC01C],
        None,
        "Checks if the entity passed is a valid monster, and if it's at low health"
        " (below 25% rounded down)\n\nr0: entity pointer\nreturn: bool",
    )

    IsSpecialStoryAlly = Symbol(
        [0x1F94C],
        [0x22FC4CC],
        None,
        "Checks if a monster is a special story ally.\n\nThis is a hard-coded check"
        " that looks at the monster's 'Joined At' field. If the value is in the range"
        " [DUNGEON_JOINED_AT_BIDOOF, DUNGEON_DUMMY_0xE3], this check will return"
        " true.\n\nr0: monster pointer\nreturn: bool",
    )

    IsExperienceLocked = Symbol(
        [0x1F96C],
        [0x22FC4EC],
        None,
        "Checks if a monster does not gain experience.\n\nThis basically just inverts"
        " IsSpecialStoryAlly, with the exception of also checking for the 'Joined At'"
        " field being DUNGEON_CLIENT (is this set for mission clients?).\n\nr0: monster"
        " pointer\nreturn: bool",
    )

    InitTeam = Symbol(
        [0x20388],
        [0x22FCF08],
        None,
        "Seems to initialize the team when entering a dungeon.\n\nr0: ?",
    )

    SpawnMonster = Symbol(
        [0x20F00],
        [0x22FDA80],
        None,
        "Spawns the given monster on a tile.\n\nr0: pointer to struct"
        " spawned_monster_data\nr1: if true, the monster cannot spawn asleep, otherwise"
        " it will randomly be asleep\nreturn: pointer to entity",
    )

    InitTeamMember = Symbol(
        [0x21230],
        [0x22FDDB0],
        None,
        "Initializes a team member. Run at the start of each floor in a dungeon.\n\nr0:"
        " Monster ID\nr1: First type\nr2: Second type\nr3: Pointer to the struct"
        " containing the data of the team member to initialize\nstack[0]: ?\nstack[1]:"
        " ?\nstack[2]: ?\nstack[3]: ?\nstack[4]: ?",
    )

    ExecuteMonsterAction = Symbol(
        [0x2235C],
        [0x22FEEDC],
        None,
        "Executes the set action for the specified monster. Used for both AI actions"
        " and player-inputted actions. If the action is not ACTION_NOTHING,"
        " ACTION_PASS_TURN, ACTION_WALK or ACTION_UNK_4, the monster's already_acted"
        " field is set to true. Includes a switch based on the action ID that performs"
        " the action, although some of them aren't handled by said swtich.\n\nr0:"
        " Pointer to monster entity",
    )

    HasStatusThatPreventsActing = Symbol(
        [0x23074],
        [0x22FFBF4],
        None,
        "Returns true if the monster has any status problem that prevents it from"
        " acting\n\nr0: Entity pointer\nreturn: True if the specified monster can't act"
        " because of a status problem, false otherwise.",
    )

    CalcSpeedStage = Symbol(
        [0x23CA0],
        [0x2300820],
        None,
        "Calculates the speed stage of a monster from its speed up/down counters. The"
        " second parameter is the weight of each counter (how many stages it will"
        " add/remove), but appears to be always 1. \nTakes modifiers into account"
        " (paralysis, snowy weather, Time Tripper). Deoxys-speed, Shaymin-sky and enemy"
        " Kecleon during a thief alert get a flat +1 always.\n\nThe calculated speed"
        " stage is both returned and saved in the monster's statuses struct.\n\nr0:"
        " pointer to entity\nr1: speed counter weight\nreturn: speed stage",
    )

    CalcSpeedStageWrapper = Symbol(
        [0x23DF8],
        [0x2300978],
        None,
        "Calls CalcSpeedStage with a speed counter weight of 1.\n\nr0: pointer to"
        " entity\nreturn: speed stage",
    )

    GetNumberOfAttacks = Symbol(
        [0x23E08],
        [0x2300988],
        None,
        "Returns the number of attacks that a monster can do in one turn (1 or"
        " 2).\n\nChecks for the abilities Swift Swim, Chlorophyll, Unburden, and for"
        " exclusive items.\n\nr0: pointer to entity\nreturns: int",
    )

    SprintfStatic = Symbol(
        [0x24174],
        [0x2300CF4],
        None,
        "Statically defined copy of sprintf(3) in overlay 29. See arm9.yml for more"
        " information.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )

    IsMonsterCornered = Symbol(
        [0x24FC4],
        [0x2301B44],
        None,
        "True if the given monster is cornered (it can't move in any direction)\n\nr0:"
        " Entity pointer\nreturn: True if the monster can't move in any direction,"
        " false otherwise.",
    )

    CanAttackInDirection = Symbol(
        [0x250E0],
        [0x2301C60],
        None,
        "Returns whether a monster can attack in a given direction.\nThe check fails if"
        " the destination tile is impassable, contains a monster that isn't of type"
        " entity_type::ENTITY_MONSTER or if the monster can't directly move from the"
        " current tile into the destination tile.\n\nr0: Entity pointer\nr1:"
        " Direction\nreturn: True if the monster can attack into the tile adjacent to"
        " them in the specified direction, false otherwise.",
    )

    CanAiMonsterMoveInDirection = Symbol(
        [0x251A4],
        [0x2301D24],
        None,
        "Checks whether an AI-controlled monster can move in the specified"
        " direction.\nAccounts for walls, other monsters on the target position and IQ"
        " skills that might prevent a monster from moving into a specific location,"
        " such as House Avoider, Trap Avoider or Lava Evader.\n\nr0: Entity"
        " pointer\nr1: Direction\nr2: (output) If movement was not possible because"
        " there was another monster on the target tile, its entity pointer is returned"
        " here\nreturn: True if the monster can move in the specified direction, false"
        " otherwise.",
    )

    ShouldMonsterRunAway = Symbol(
        [0x25464],
        [0x2301FE4],
        None,
        "Checks if a monster should run away from other monsters\n\nr0: Entity"
        " pointer\nreturn: True if the monster should run away, false otherwise",
    )

    ShouldMonsterRunAwayVariation = Symbol(
        [0x25554],
        [0x23020D4],
        None,
        "Calls ShouldMonsterRunAway and returns its result. It also calls another"
        " function if the result was true.\n\nr0: Entity pointer\nr1: ?\nreturn: Result"
        " of the call to ShouldMonsterRunAway",
    )

    NoGastroAcidStatus = Symbol(
        [0x25B88],
        [0x2302708],
        None,
        "Checks if a monster does not have the Gastro Acid status.\n\nr0: entity"
        " pointer\nreturn: bool",
    )

    AbilityIsActive = Symbol(
        [0x25BBC],
        [0x230273C],
        None,
        "Checks if a monster has a certain ability that isn't disabled by Gastro"
        " Acid.\n\nr0: entity pointer\nr1: ability ID\nreturn: bool",
    )

    LevitateIsActive = Symbol(
        [0x25CC4],
        [0x2302844],
        None,
        "Checks if a monster is levitating (has the effect of Levitate and Gravity is"
        " not active).\n\nr0: pointer to entity\nreturn: bool",
    )

    MonsterIsType = Symbol(
        [0x25CFC],
        [0x230287C],
        None,
        "Checks if a monster is a given type.\n\nr0: entity pointer\nr1: type"
        " ID\nreturn: bool",
    )

    CanSeeInvisibleMonsters = Symbol(
        [0x25D98],
        [0x2302918],
        None,
        "Returns whether a certain monster can see other invisible monsters.\nTo be"
        " precise, this function returns true if the monster is holding Goggle Specs or"
        " if it has the status status::STATUS_EYEDROPS.\n\nr0: Entity pointer\nreturn:"
        " True if the monster can see invisible monsters.",
    )

    HasDropeyeStatus = Symbol(
        [0x25DFC],
        [0x230297C],
        None,
        "Returns whether a certain monster is under the effect of"
        " status::STATUS_DROPEYE.\n\nr0: Entity pointer\nreturn: True if the monster"
        " has dropeye status.",
    )

    IqSkillIsEnabled = Symbol(
        [0x25E2C],
        [0x23029AC],
        None,
        "Checks if a monster has a certain IQ skill enabled.\n\nr0: entity pointer\nr1:"
        " IQ skill ID\nreturn: bool",
    )

    GetMoveTypeForMonster = Symbol(
        [0x26128],
        [0x2302CA8],
        None,
        "Check the type of a move when used by a certain monster. Accounts for special"
        " cases such as Hidden Power, Weather Ball, the regular attack...\n\nr0: Entity"
        " pointer\nr1: Pointer to move data\nreturn: Type of the move",
    )

    GetMovePower = Symbol(
        [0x261C8],
        [0x2302D48],
        None,
        "Gets the power of a move, factoring in Ginseng/Space Globe boosts.\n\nr0: user"
        " pointer\nr1: move pointer\nreturn: move power",
    )

    AddExpSpecial = Symbol(
        [0x263E8],
        [0x2302F68],
        None,
        "Adds to a monster's experience points, subject to experience boosting"
        " effects.\n\nThis function appears to be called only under special"
        " circumstances. Possibly when granting experience from damage (e.g., Joy"
        " Ribbon)?\n\nInterestingly, the parameter in r0 isn't actually used. This"
        " might be a compiler optimization to avoid shuffling registers, since this"
        " function might be called alongside lots of other functions that have both the"
        " attacker and defender as the first two arguments.\n\nr0: attacker"
        " pointer\nr1: defender pointer\nr2: base experience gain, before boosts",
    )

    EnemyEvolution = Symbol(
        [0x265A8],
        [0x2303128],
        None,
        "Checks if the specified enemy should evolve because it just defeated an ally,"
        " and if so, attempts to evolve it.\n\nr0: Pointer to the enemy to check",
    )

    EvolveMonster = Symbol(
        [0x27B28],
        [0x23046A8],
        None,
        "Makes the specified monster evolve into the specified species.\n\nr0: Pointer"
        " to the entity to evolve\nr1: ?\nr2: Species to evolve into",
    )

    GetSleepAnimationId = Symbol(
        [0x28960],
        [0x23054E0],
        None,
        "Returns the animation id to be applied to a monster that has the sleep,"
        " napping, nightmare or bide status.\n\nReturns a different animation for"
        " sudowoodo and for monsters with infinite sleep turns (0x7F).\n\nr0: pointer"
        " to entity\nreturn: animation ID",
    )

    DisplayActions = Symbol(
        [0x28E8C],
        [0x2305A0C],
        None,
        "Graphically displays any pending actions that have happened but haven't been"
        " shown on screen yet. All actions are displayed at the same time. For example,"
        " this delayed display system is used to display multiple monsters moving at"
        " once even though they take turns sequentially.\n\nr0: Pointer to an entity."
        " Can be null.\nreturns: Seems to be true if there were any pending actions to"
        " display.",
    )

    EndFrozenClassStatus = Symbol(
        [0x2A104],
        [0x2306C84],
        None,
        "Cures the target's freeze, shadow hold, ingrain, petrified, constriction or"
        " wrap (both as user and as target) status due to the action of the"
        " user.\n\nr0: pointer to user\nr1: pointer to target\nr2: if true, the event"
        " will be printed to the log",
    )

    EndCringeClassStatus = Symbol(
        [0x2A280],
        [0x2306E00],
        None,
        "Cures the target's cringe, confusion, cowering, pause, taunt, encore or"
        " infatuated status due to the action of the user, and prints the event to the"
        " log.\n\nr0: pointer to user\nr1: pointer to target",
    )

    RunMonsterAi = Symbol(
        [0x2C1EC],
        [0x2308D6C],
        None,
        "Runs the AI for a single monster to determine whether the monster can act and"
        " which action it should perform if so\n\nr0: Pointer to monster\nr1: ?",
    )

    ApplyDamage = Symbol(
        [0x2CE8C],
        [0x2309A0C],
        None,
        "Applies damage to a monster. Displays the damage animation, lowers its health"
        " and handles reviving if applicable.\nThe EU version has some additional"
        " checks related to printing fainting messages under specific"
        " circumstances.\n\nr0: Attacker pointer\nr1: Defender pointer\nr2: Pointer to"
        " the damage_data struct that contains info about the damage to deal\nr3:"
        " ?\nstack[0]: ?\nstack[1]: Pointer to some struct. The first byte contains the"
        " ID of the move used.\nreturn: True if the target fainted (reviving does not"
        " count as fainting)",
    )

    GetTypeMatchup = Symbol(
        [0x2EB4C],
        [0x230B6CC],
        None,
        "Gets the type matchup for a given combat interaction.\n\nNote that the actual"
        " monster's types on the attacker and defender pointers are not used; the"
        " pointers are only used to check conditions. The actual type matchup table"
        " lookup is done solely using the attack and target type parameters.\n\nThis"
        " factors in some conditional effects like exclusive items, statuses, etc."
        " There's some weirdness with the Ghost type; see the comment for struct"
        " type_matchup_table.\n\nr0: attacker pointer\nr1: defender pointer\nr2: target"
        " type index (0 the target's first type, 1 for the target's second type)\nr3:"
        " attack type\nreturn: enum type_matchup",
    )

    CalcDamage = Symbol(
        [0x2FAA0],
        [0x230C620],
        None,
        "Probably the damage calculation function.\n\nr0: attacker pointer\nr1:"
        " defender pointer\nr2: attack type\nr3: attack power\nstack[0]: crit"
        " chance\nstack[1]: [output] struct containing info about the damage"
        " calculation\nstack[2]: damage multiplier (as a binary fixed-point number with"
        " 8 fraction bits)\nstack[3]: move ID\nstack[4]: ?",
    )

    CalcRecoilDamageFixed = Symbol(
        [0x31080],
        [0x230DC00],
        None,
        "Appears to calculate recoil damage to a monster.\n\nThis function wraps"
        " CalcDamageFixed using the monster as both the attacker and the defender,"
        " after doing some basic checks (like if the monster is already at 0 HP) and"
        " applying a boost from the Reckless ability if applicable.\n\nr0: entity"
        " pointer\nr1: fixed damage\nr2: ?\nr3: [output] struct containing info about"
        " the damage calculation\nstack[0]: move ID (interestingly, this doesn't seem"
        " to be used by the function)\nstack[1]: attack type\nstack[2]: ?\nstack[3]:"
        " message type\nothers: ?",
    )

    CalcDamageFixed = Symbol(
        [0x31134],
        [0x230DCB4],
        None,
        "Appears to calculate damage from a fixed-damage effect.\n\nr0: attacker"
        " pointer\nr1: defender pointer\nr2: fixed damage\nr3: ?\nstack[0]: [output]"
        " struct containing info about the damage calculation\nstack[1]: attack"
        " type\nstack[2]: move category\nstack[3]: ?\nstack[4]: message"
        " type\nothers: ?",
    )

    CalcDamageFixedNoCategory = Symbol(
        [0x3129C],
        [0x230DE1C],
        None,
        "A wrapper around CalcDamageFixed with the move category set to none.\n\nr0:"
        " attacker pointer\nr1: defender pointer\nr2: fixed damage\nstack[0]: [output]"
        " struct containing info about the damage calculation\nstack[1]: attack"
        " type\nothers: ?",
    )

    CalcDamageFixedWrapper = Symbol(
        [0x312E8],
        [0x230DE68],
        None,
        "A wrapper around CalcDamageFixed.\n\nr0: attacker pointer\nr1: defender"
        " pointer\nr2: fixed damage\nstack[0]: [output] struct containing info about"
        " the damage calculation\nstack[1]: attack type\nstack[2]: move"
        " category\nothers: ?",
    )

    ResetDamageCalcScratchSpace = Symbol(
        [0x3141C],
        [0x230DF9C],
        None,
        "CalcDamage seems to use scratch space of some kind, which this function"
        " zeroes.\n\nNo params.",
    )

    TrySpawnMonsterAndTickSpawnCounter = Symbol(
        [0x325B0],
        [0x230F130],
        None,
        "First ticks up the spawn counter, and if it's equal or greater than the spawn"
        " cooldown, it will try to spawn an enemy if the number of enemies is below the"
        " spawn cap.\n\nIf the spawn counter is greater than 900, it will instead"
        " perform the special spawn caused by the ability Illuminate.\n\nNo params.",
    )

    AuraBowIsActive = Symbol(
        [0x335BC],
        [0x231013C],
        None,
        "Checks if a monster is holding an aura bow that isn't disabled by"
        " Klutz.\n\nr0: entity pointer\nreturn: bool",
    )

    ExclusiveItemOffenseBoost = Symbol(
        [0x3366C],
        [0x23101EC],
        None,
        "Gets the exclusive item boost for attack/special attack for a monster\n\nr0:"
        " entity pointer\nr1: move category index (0 for physical, 1 for"
        " special)\nreturn: boost",
    )

    ExclusiveItemDefenseBoost = Symbol(
        [0x3367C],
        [0x23101FC],
        None,
        "Gets the exclusive item boost for defense/special defense for a monster\n\nr0:"
        " entity pointer\nr1: move category index (0 for physical, 1 for"
        " special)\nreturn: boost",
    )

    TickNoSlipCap = Symbol(
        [0x33A84],
        [0x2310604],
        None,
        "Checks if the entity is a team member and holds the No-Slip Cap, and if so"
        " attempts to make one item in the bag sticky.\n\nr0: pointer to entity",
    )

    TickStatusAndHealthRegen = Symbol(
        [0x34F68],
        [0x2311AE8],
        None,
        "Applies the natural HP regen effect by taking modifiers into account (Poison"
        " Heal, Heal Ribbon, weather-related regen). Then it ticks down counters for"
        " volatile status effects, and heals them if the counter reached zero.\n\nr0:"
        " pointer to entity",
    )

    InflictSleepStatusSingle = Symbol(
        [0x35704],
        [0x2312284],
        None,
        "This is called by TryInflictSleepStatus.\n\nr0: entity pointer\nr1: number of"
        " turns",
    )

    TryInflictSleepStatus = Symbol(
        [0x357B8],
        [0x2312338],
        None,
        "Inflicts the Sleep status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: number of turns\nr3: flag"
        " to log a message on failure",
    )

    TryInflictNightmareStatus = Symbol(
        [0x35B2C],
        [0x23126AC],
        None,
        "Inflicts the Nightmare status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: number"
        " of turns",
    )

    TryInflictNappingStatus = Symbol(
        [0x35C40],
        [0x23127C0],
        None,
        "Inflicts the Napping status condition (from Rest) on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: number"
        " of turns",
    )

    TryInflictYawningStatus = Symbol(
        [0x35D50],
        [0x23128D0],
        None,
        "Inflicts the Yawning status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: number of turns",
    )

    TryInflictSleeplessStatus = Symbol(
        [0x35E60],
        [0x23129E0],
        None,
        "Inflicts the Sleepless status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    TryInflictPausedStatus = Symbol(
        [0x35F4C],
        [0x2312ACC],
        None,
        "Inflicts the Paused status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: ?\nr3: number of"
        " turns\nstack[0]: flag to log a message on failure\nstack[1]: flag to only"
        " perform the check for inflicting without actually inflicting\nreturn: Whether"
        " or not the status could be inflicted",
    )

    TryInflictInfatuatedStatus = Symbol(
        [0x3608C],
        [0x2312C0C],
        None,
        "Inflicts the Infatuated status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    TryInflictBurnStatus = Symbol(
        [0x36218],
        [0x2312D98],
        None,
        "Inflicts the Burn status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to apply some"
        " special effect alongside the burn?\nr3: flag to log a message on"
        " failure\nstack[0]: flag to only perform the check for inflicting without"
        " actually inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictBurnStatusWholeTeam = Symbol(
        [0x364F8],
        [0x2313078],
        None,
        "Inflicts the Burn status condition on all team members if possible.\n\nNo"
        " params.",
    )

    TryInflictPoisonedStatus = Symbol(
        [0x36544],
        [0x23130C4],
        None,
        "Inflicts the Poisoned status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictBadlyPoisonedStatus = Symbol(
        [0x3681C],
        [0x231339C],
        None,
        "Inflicts the Badly Poisoned status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    TryInflictFrozenStatus = Symbol(
        [0x36AD8],
        [0x2313658],
        None,
        "Inflicts the Frozen status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure",
    )

    TryInflictConstrictionStatus = Symbol(
        [0x36D00],
        [0x2313880],
        None,
        "Inflicts the Constriction status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2:"
        " animation ID\nr3: flag to log a message on failure",
    )

    TryInflictShadowHoldStatus = Symbol(
        [0x36E58],
        [0x23139D8],
        None,
        "Inflicts the Shadow Hold (AKA Immobilized) status condition on a target"
        " monster if possible.\n\nr0: user entity pointer\nr1: target entity"
        " pointer\nr2: flag to log a message on failure",
    )

    TryInflictIngrainStatus = Symbol(
        [0x37010],
        [0x2313B90],
        None,
        "Inflicts the Ingrain status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer",
    )

    TryInflictWrappedStatus = Symbol(
        [0x370D4],
        [0x2313C54],
        None,
        "Inflicts the Wrapped status condition on a target monster if possible.\n\nThis"
        " also gives the user the Wrap status (Wrapped around foe).\n\nr0: user entity"
        " pointer\nr1: target entity pointer",
    )

    FreeOtherWrappedMonsters = Symbol(
        [0x372D0],
        [0x2313E50],
        None,
        "Frees from the wrap status all monsters which are wrapped by/around the"
        " monster passed as parameter.\n\nr0: pointer to entity",
    )

    TryInflictPetrifiedStatus = Symbol(
        [0x3734C],
        [0x2313ECC],
        None,
        "Inflicts the Petrified status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    LowerOffensiveStat = Symbol(
        [0x374DC],
        [0x231405C],
        None,
        "Lowers the specified offensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of"
        " stages\nstack[0]: ?\nstack[1]: ?",
    )

    LowerDefensiveStat = Symbol(
        [0x376F4],
        [0x2314274],
        None,
        "Lowers the specified defensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of"
        " stages\nstack[0]: ?\nstack[1]: ?",
    )

    BoostOffensiveStat = Symbol(
        [0x3787C],
        [0x23143FC],
        None,
        "Boosts the specified offensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of stages",
    )

    BoostDefensiveStat = Symbol(
        [0x379E8],
        [0x2314568],
        None,
        "Boosts the specified defensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of stages",
    )

    ApplyOffensiveStatMultiplier = Symbol(
        [0x37C20],
        [0x23147A0],
        None,
        "Applies a multiplier to the specified offensive stat on the target"
        " monster.\n\nThis affects struct"
        " monster_stat_modifiers::offensive_multipliers, for moves like Charm and"
        " Memento.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: stat"
        " index\nr3: multiplier\nstack[0]: ?",
    )

    ApplyDefensiveStatMultiplier = Symbol(
        [0x37E44],
        [0x23149C4],
        None,
        "Applies a multiplier to the specified defensive stat on the target"
        " monster.\n\nThis affects struct"
        " monster_stat_modifiers::defensive_multipliers, for moves like Screech.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: stat index\nr3:"
        " multiplier\nstack[0]: ?",
    )

    BoostHitChanceStat = Symbol(
        [0x37FC4],
        [0x2314B44],
        None,
        "Boosts the specified hit chance stat (accuracy or evasion) on the target"
        " monster.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: stat"
        " index",
    )

    LowerHitChanceStat = Symbol(
        [0x3810C],
        [0x2314C8C],
        None,
        "Lowers the specified hit chance stat (accuracy or evasion) on the target"
        " monster.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: stat"
        " index\nr3: ?",
    )

    TryInflictCringeStatus = Symbol(
        [0x382C8],
        [0x2314E48],
        None,
        "Inflicts the Cringe status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictParalysisStatus = Symbol(
        [0x38424],
        [0x2314FA4],
        None,
        "Inflicts the Paralysis status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    BoostSpeed = Symbol(
        [0x386F0],
        [0x2315270],
        None,
        "Boosts the speed of the target monster.\n\nIf the number of turns specified is"
        " 0, a random turn count will be selected using the default"
        " SPEED_BOOST_DURATION_RANGE.\n\nr0: user entity pointer\nr1: target entity"
        " pointer\nr2: number of stages\nr3: number of turns\nstack[0]: flag to log a"
        " message on failure",
    )

    BoostSpeedOneStage = Symbol(
        [0x3881C],
        [0x231539C],
        None,
        "A wrapper around BoostSpeed with the number of stages set to 1.\n\nr0: user"
        " entity pointer\nr1: target entity pointer\nr2: number of turns\nr3: flag to"
        " log a message on failure",
    )

    LowerSpeed = Symbol(
        [0x38834],
        [0x23153B4],
        None,
        "Lowers the speed of the target monster.\n\nr0: user entity pointer\nr1: target"
        " entity pointer\nr2: number of stages\nr3: flag to log a message on failure",
    )

    TrySealMove = Symbol(
        [0x3899C],
        [0x231551C],
        None,
        "Seals one of the target monster's moves. The move to be sealed is randomly"
        " selected.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nreturn: Whether or not a move was sealed",
    )

    BoostOrLowerSpeed = Symbol(
        [0x38B0C],
        [0x231568C],
        None,
        "Randomly boosts or lowers the speed of the target monster by one stage with"
        " equal probability.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    ResetHitChanceStat = Symbol(
        [0x38B6C],
        [0x23156EC],
        None,
        "Resets the specified hit chance stat (accuracy or evasion) back to normal on"
        " the target monster.\n\nr0: user entity pointer\nr1: target entity"
        " pointer\nr2: stat index\nr3: ?",
    )

    TryActivateQuickFeet = Symbol(
        [0x38CFC],
        [0x231587C],
        None,
        "Activate the Quick Feet ability on the defender, if the monster has it and"
        " it's active.\n\nr0: attacker pointer\nr1: defender pointer\nreturn: bool,"
        " whether or not the ability was activated",
    )

    TryInflictConfusedStatus = Symbol(
        [0x38E18],
        [0x2315998],
        None,
        "Inflicts the Confused status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictCoweringStatus = Symbol(
        [0x3914C],
        [0x2315CCC],
        None,
        "Inflicts the Cowering status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryIncreaseHp = Symbol(
        [0x391C4],
        [0x2315D44],
        None,
        "Restore HP and possibly boost max HP of the target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: HP to restore\nr3: max HP"
        " boost\nstack[0]: flag to log a message on failure\nreturn: Success flag",
    )

    TryInflictLeechSeedStatus = Symbol(
        [0x396CC],
        [0x231624C],
        None,
        "Inflicts the Leech Seed status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    TryInflictDestinyBond = Symbol(
        [0x39930],
        [0x23164B0],
        None,
        "Inflicts the Destiny Bond status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    IsBlinded = Symbol(
        [0x3B6C4],
        [0x2318244],
        None,
        "Returns true if the monster has the blinded status (see statuses::blinded), or"
        " if it is not the leader and is holding Y-Ray Specs.\n\nr0: pointer to"
        " entity\nr1: flag for whether to check for the held item\nreturn: bool",
    )

    RestoreMovePP = Symbol(
        [0x3BB00],
        [0x2318680],
        None,
        "Restores the PP of all the target's moves by the specified amount.\n\nr0: user"
        " entity pointer\nr1: target entity pointer\nr2: PP to restore\nr3: flag to"
        " suppress message logging",
    )

    SetReflectDamageCountdownTo4 = Symbol(
        [0x3C2A0],
        [0x2318E20],
        None,
        "Sets the monster's reflect damage countdown to a global value (0x4).\n\nr0:"
        " pointer to entity",
    )

    HasConditionalGroundImmunity = Symbol(
        [0x3C92C],
        [0x23194AC],
        None,
        "Checks if a monster is currently immune to Ground-type moves for reasons other"
        " than typing and ability.\n\nThis includes checks for Gravity and Magnet"
        " Rise.\n\nr0: entity pointer\nreturn: bool",
    )

    Conversion2IsActive = Symbol(
        [0x3D6F4],
        [0x231A274],
        None,
        "Checks if the monster is under the effect of Conversion 2 (its type was"
        " changed).\n\nReturns 1 if the effects is a status, 2 if it comes from an"
        " exclusive item, 0 otherwise.\n\nr0: pointer to entity\nreturn: int",
    )

    AiConsiderMove = Symbol(
        [0x3D760],
        [0x231A2E0],
        None,
        "The AI uses this function to check if a move has any potential targets, to"
        " calculate the list of potential targets and to calculate the move's special"
        " weight.\nThis weight will be higher if the pokémon has weak-type picker and"
        " the target is weak to the move (allies only, enemies always get a result of 1"
        " even if the move is super effective). More things could affect the"
        " result.\nThis function also sets the flag can_be_used on the ai_possible_move"
        " struct if it makes sense to use it.\nMore research is needed. There's more"
        " documentation about this special weight. Does all the documented behavior"
        " happen in this function?\n\nr0: ai_possible_move struct for this move\nr1:"
        " Entity pointer\nr2: Move pointer\nreturn: Move's calculated special weight",
    )

    TryAddTargetToAiTargetList = Symbol(
        [0x3DE90],
        [0x231AA10],
        None,
        "Checks if the specified target is eligible to be targeted by the AI and if so"
        " adds it to the list of targets. This function also fills an array that seems"
        " to contain the directions in which the user should turn to look at each of"
        " the targets in the list, as well as a third unknown array.\n\nr0: Number of"
        " existing targets in the list\nr1: Move's AI range field\nr2: User entity"
        " pointer\nr3: Target entity pointer\nstack[0]: Move pointer\nstack[1]:"
        " check_all_conditions parameter to pass to IsAiTargetEligible\nreturn: New"
        " number of targets in the target list",
    )

    IsAiTargetEligible = Symbol(
        [0x3DF84],
        [0x231AB04],
        None,
        "Checks if a given target is eligible to be targeted by the AI with a certain"
        " move\n\nr0: Move's AI range field\nr1: User entity pointer\nr2: Target entity"
        " pointer\nr3: Move pointer\nstack[0]: True to check all the possible"
        " move_ai_condition values, false to only check for"
        " move_ai_condition::AI_CONDITION_RANDOM (if the move has a different ai"
        " condition, the result will be false).\nreturn: True if the target is"
        " eligible, false otherwise",
    )

    IsTargetInRange = Symbol(
        [0x3E574],
        [0x231B0F4],
        None,
        "Returns true if the target is within range of the user's move, false"
        " otherwise.\n\nIf the user does not have Course Checker, it simply checks if"
        " the distance between user and target is less or equal than the move"
        " range.\nOtherwise, it will iterate through all tiles in the direction"
        " specified, checking for walls or other monsters in the way, and return false"
        " if they are found.\n\nr0: user pointer\nr1: target pointer\nr2: direction"
        " ID\nr3: move range (in number of tiles)",
    )

    GetEntityMoveTargetAndRange = Symbol(
        [0x3EB8C],
        [0x231B70C],
        None,
        "Gets the move target-and-range field when used by a given entity. See struct"
        " move_target_and_range in the C headers.\n\nr0: entity pointer\nr1: move"
        " pointer\nr2: AI flag (same as GetMoveTargetAndRange)\nreturn: move target and"
        " range",
    )

    ApplyItemEffect = Symbol(
        [0x3F56C],
        [0x231C0EC],
        None,
        "Seems to apply an item's effect via a giant switch statement?\n\nr3: attacker"
        " pointer\nstack[0]: defender pointer\nstack[1]: thrown item"
        " pointer\nothers: ?",
    )

    ViolentSeedBoost = Symbol(
        [0x40D04],
        [0x231D884],
        None,
        "Applies the Violent Seed boost to an entity.\n\nr0: attacker pointer\nr1:"
        " defender pointer",
    )

    ApplyGummiBoostsDungeonMode = Symbol(
        [0x40FA8],
        [0x231DB28],
        None,
        "Applies the IQ and possible stat boosts from eating a Gummi to the target"
        " monster.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: Gummi"
        " type ID\nr3: Stat boost amount, if a random stat boost occurs",
    )

    GetMaxPpWrapper = Symbol(
        [0x428D8],
        [0x231F458],
        None,
        "Gets the maximum PP for a given move. A wrapper around the function in the ARM"
        " 9 binary.\n\nr0: move pointer\nreturn: max PP for the given move, capped"
        " at 99",
    )

    MoveIsNotPhysical = Symbol(
        [0x42900],
        [0x231F480],
        None,
        "Checks if a move isn't a physical move.\n\nr0: move ID\nreturn: bool",
    )

    TryPounce = Symbol(
        [0x43B08],
        [0x2320688],
        None,
        "Makes the target monster execute the Pounce action in a given direction if"
        " possible.\n\nIf the direction ID is 8, the target will pounce in the"
        " direction it's currently facing.\n\nr0: user entity pointer\nr1: target"
        " entity pointer\nr2: direction ID",
    )

    TryBlowAway = Symbol(
        [0x43CC8],
        [0x2320848],
        None,
        "Blows away the target monster in a given direction if possible.\n\nr0: user"
        " entity pointer\nr1: target entity pointer\nr2: direction ID",
    )

    TryWarp = Symbol(
        [0x44BF0],
        [0x2321770],
        None,
        "Makes the target monster warp if possible.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: warp type\nr3: position (if warp type is"
        " position-based)",
    )

    MoveHitCheck = Symbol(
        [0x47B30],
        [0x23246B0],
        None,
        "Determines if a move used hits or misses the target. It gets called twice per"
        " target, once with r3 = false and a second time with r3 = true.\n\nr0:"
        " Attacker\nr1: Defender\nr2: Pointer to move data\nr3: True if the move's"
        " first accuracy (accuracy1) should be used, false if its second accuracy"
        " (accuracy2) should be used instead.\nreturns: True if the move hits, false if"
        " it misses.",
    )

    DungeonRandOutcomeUserTargetInteraction = Symbol(
        [0x4881C],
        [0x232539C],
        None,
        "Like DungeonRandOutcome, but specifically for user-target"
        " interactions.\n\nThis modifies the underlying random process depending on"
        " factors like Serene Grace, and whether or not either entity has"
        " fainted.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: base"
        " success percentage (100*p). 0 is treated specially and guarantees success.",
    )

    DungeonRandOutcomeUserAction = Symbol(
        [0x48908],
        [0x2325488],
        None,
        "Like DungeonRandOutcome, but specifically for user actions.\n\nThis modifies"
        " the underlying random process to factor in Serene Grace (and checks whether"
        " the user is a valid entity).\n\nr0: entity pointer\nr1: base success"
        " percentage (100*p). 0 is treated specially and guarantees success.",
    )

    CanAiUseMove = Symbol(
        [0x4895C],
        [0x23254DC],
        None,
        "Checks if an AI-controlled monster can use a move.\nWill return false if the"
        " any of the flags move::f_exists, move::f_subsequent_in_link_chain or"
        " move::f_disabled is true. The function does not check if the flag"
        " move::f_enabled_for_ai is set. This function also returns true if the call to"
        " CanMonsterUseMove is true.\nThe function contains a loop that is supposed to"
        " check other moves after the specified one, but the loop breaks after it finds"
        " a move that isn't linked, which is always true given the checks in place at"
        " the start of the function.\n\nr0: Entity pointer\nr1: Move index\nr2:"
        " extra_checks parameter when calling CanMonsterUseMove\nreturn: True if the AI"
        " can use the move (not accounting for move::f_enabled_for_ai)",
    )

    CanMonsterUseMove = Symbol(
        [0x48A0C],
        [0x232558C],
        None,
        "Checks if a monster can use the given move.\nWill always return true for the"
        " regular attack. Will return false if the move if the flag move::f_disabled is"
        " true, if the flag move::f_sealed is true. More things will be checked if the"
        " extra_checks parameter is true.\n\nr0: Entity pointer\nr1: Move pointer\nr2:"
        " True to check whether the move is out of PP, whether it can be used under the"
        " taunted status and whether the encore status prevents using the move\nreturn:"
        " True if the monster can use the move, false otherwise.",
    )

    UpdateMovePp = Symbol(
        [0x48C74],
        [0x23257F4],
        None,
        "Updates the PP of any moves that were used by a monster, if PP should be"
        " consumed.\n\nr0: entity pointer\nr1: flag for whether or not PP should be"
        " consumed",
    )

    LowerSshort = Symbol(
        [0x48D4C],
        [0x23258CC],
        None,
        "Gets the lower 2 bytes of a 4-byte number and interprets it as a signed"
        " short.\n\nr0: 4-byte number x\nreturn: (short) x",
    )

    GetMoveAnimationId = Symbol(
        [0x499F8],
        [0x2326578],
        None,
        "Returns the move animation ID that should be played for a move.\nIt contains a"
        " check for weather ball. After that, if the parameter"
        " should_play_alternative_animation is false, the move ID is returned. If it's"
        " true, there's a bunch of manual ID checks that result on a certain hardcoded"
        " return value.\n\nr0: Move ID\nr1: Apparent weather for the monster who used"
        " the move\nr2: Result of ShouldMovePlayADifferentAnimation\nreturn: Move"
        " animation ID",
    )

    ShouldMovePlayAlternativeAnimation = Symbol(
        [0x49B60],
        [0x23266E0],
        None,
        "Checks whether a moved used by a monster should play its alternative"
        " animation. Includes checks for Curse, Snore, Sleep Talk, Solar Beam and"
        " 2-turn moves.\n\nr0: Pointer to the entity that used the move\nr1: Move"
        " pointer\nreturn: True if the move should play its alternative animation",
    )

    DealDamageWithRecoil = Symbol(
        [0x4BE20],
        [0x23289A0],
        None,
        "Deals damage from a move or item used by an attacking monster on a defending"
        " monster, and also deals recoil damage to the attacker.\n\nr0: attacker"
        " pointer\nr1: defender pointer\nr2: move\nr3: item ID\nreturn: bool, whether"
        " or not damage was dealt",
    )

    ExecuteMoveEffect = Symbol(
        [0x52724],
        [0x232F2A4],
        None,
        "Handles the effects that happen after a move is used. Includes a loop that is"
        " run for each target, mutiple ability checks and the giant switch statement"
        " that executes the effect of the move used given its ID.\n\nr0: pointer to"
        " some struct\nr1: attacker pointer\nr2: pointer to move data\nr3:"
        " ?\nstack[0]: ?",
    )

    DealDamage = Symbol(
        [0x569E0],
        [0x2333560],
        None,
        "Deals damage from a move or item used by an attacking monster on a defending"
        " monster.\n\nr0: attacker pointer\nr1: defender pointer\nr2: move\nr3: damage"
        " multiplier (as a binary fixed-point number with 8 fraction bits)\nstack[0]:"
        " item ID\nreturn: amount of damage dealt",
    )

    CalcDamageProjectile = Symbol(
        [0x56B0C],
        [0x233368C],
        None,
        "Appears to calculate damage from a variable-damage projectile.\n\nr0: entity"
        " pointer 1?\nr1: entity pointer 2?\nr2: move pointer\nr3: move"
        " power\nothers: ?",
    )

    CalcDamageFinal = Symbol(
        [0x56C2C],
        [0x23337AC],
        None,
        "Last function called by DealDamage to determine the final damage dealt by the"
        " move. The result of this call is the return value of DealDamage. \n\nr0:"
        " Attacker pointer\nr1: Defender pointer\nr2: Move pointer\nr3: ?\nstack[0]:"
        " Pointer to some struct. The first byte contains the ID of the move used.",
    )

    StatusCheckerCheck = Symbol(
        [0x56F34],
        [0x2333AB4],
        None,
        "Determines if using a given move against its intended targets would be"
        " redundant because all of them already have the effect caused by said"
        " move.\n\nr0: Pointer to the entity that is considering using the move\nr1:"
        " Move pointer\nreturn: True if it makes sense to use the move, false if it"
        " would be redundant given the effects it causes and the effects that all the"
        " targets already have.",
    )

    GetApparentWeather = Symbol(
        [0x58BC8],
        [0x2335748],
        None,
        "Get the weather, as experienced by a specific entity.\n\nr0: entity"
        " pointer\nreturn: weather ID",
    )

    TryWeatherFormChange = Symbol(
        [0x59030],
        [0x2335BB0],
        None,
        "Tries to change a monster into one of its weather-related alternative forms."
        " Applies to Castform and Cherrim, and checks for their unique"
        " abilities.\n\nr0: pointer to entity",
    )

    GetTile = Symbol(
        [0x5A14C],
        [0x2336CCC],
        None,
        "Get the tile at some position. If the coordinates are out of bounds, returns a"
        " default tile.\n\nr0: x position\nr1: y position\nreturn: tile pointer",
    )

    GetTileSafe = Symbol(
        [0x5A1B4],
        [0x2336D34],
        None,
        "Get the tile at some position. If the coordinates are out of bounds, returns a"
        " pointer to a copy of the default tile.\n\nr0: x position\nr1: y"
        " position\nreturn: tile pointer",
    )

    GetStairsRoom = Symbol(
        [0x5A478],
        [0x2336FF8],
        None,
        "Returns the index of the room that contains the stairs\n\nreturn: Room index",
    )

    GravityIsActive = Symbol(
        [0x5C3E0],
        [0x2338F60],
        None,
        "Checks if gravity is active on the floor.\n\nreturn: bool",
    )

    IsSecretBazaar = Symbol(
        [0x5C614],
        [0x2339194],
        None,
        "Checks if the current floor is the Secret Bazaar.\n\nreturn: bool",
    )

    IsSecretRoom = Symbol(
        [0x5C6AC],
        [0x233922C],
        None,
        "Checks if the current floor is the Secret Room fixed floor (from hidden"
        " stairs).\n\nreturn: bool",
    )

    IsSecretFloor = Symbol(
        [0x5C6D4],
        [0x2339254],
        None,
        "Checks if the current floor is a secret bazaar or a secret room.\n\nreturn:"
        " bool",
    )

    GetDungeonGenInfoUnk0C = Symbol(
        [0x5C8D0], [0x2339450], None, "return: dungeon_generation_info::field_0xc"
    )

    GetMinimapData = Symbol(
        [0x5D168],
        [0x2339CE8],
        None,
        "Returns a pointer to the minimap_display_data struct in the dungeon"
        " struct.\n\nreturn: minimap_display_data*",
    )

    SetMinimapDataE447 = Symbol(
        [0x5E268],
        [0x233ADE8],
        None,
        "Sets minimap_display_data::field_0xE447 to the specified value\n\nr0: Value to"
        " set the field to",
    )

    GetMinimapDataE447 = Symbol(
        [0x5E280],
        [0x233AE00],
        None,
        "Exclusive to the EU ROM. Returns"
        " minimap_display_data::field_0xE447.\n\nreturn:"
        " minimap_display_data::field_0xE447",
    )

    SetMinimapDataE448 = Symbol(
        [0x5E294],
        [0x233AE14],
        None,
        "Sets minimap_display_data::field_0xE448 to the specified value\n\nr0: Value to"
        " set the field to",
    )

    LoadFixedRoomDataVeneer = Symbol(
        [0x5E688],
        [0x233B208],
        None,
        "Likely a linker-generated veneer for LoadFixedRoomData.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nNo"
        " params.",
    )

    IsNormalFloor = Symbol(
        [0x5E6B8],
        [0x233B238],
        None,
        "Checks if the current floor is a normal layout.\n\n'Normal' means any layout"
        " that is NOT one of the following:\n- Hidden stairs floors\n- Golden"
        " Chamber\n- Challenge Request floor\n- Outlaw hideout\n- Treasure Memo"
        " floor\n- Full-room fixed floors (ID < 0xA5) [0xA5 == Sealed"
        " Chamber]\n\nreturn: bool",
    )

    GenerateFloor = Symbol(
        [0x5E73C],
        [0x233B2BC],
        None,
        "This is the master function that generates the dungeon floor.\n\nVery loosely"
        " speaking, this function first tries to generate a valid floor layout. Then it"
        " tries to spawn entities in a valid configuration. Finally, it performs"
        " cleanup and post-processing depending on the dungeon.\n\nIf a spawn"
        " configuration is invalid, the entire floor layout is scrapped and"
        " regenerated. If the generated floor layout is invalid 10 times in a row, or a"
        " valid spawn configuration isn't generated within 10 attempts, the generation"
        " algorithm aborts and the default one-room Monster House floor is generated as"
        " a fallback.\n\nNo params.",
    )

    GetTileTerrain = Symbol(
        [0x5EEDC],
        [0x233BA5C],
        None,
        "Gets the terrain type of a tile.\n\nr0: tile pointer\nreturn: terrain ID",
    )

    DungeonRand100 = Symbol(
        [0x5EEE8],
        [0x233BA68],
        None,
        "Compute a pseudorandom integer on the interval [0, 100) using the dungeon"
        " PRNG.\n\nreturn: pseudorandom integer",
    )

    FlagHallwayJunctions = Symbol(
        [0x5EF70],
        [0x233BAF0],
        None,
        "Sets the junction flag (bit 3 of the terrain flags) on any hallway junction"
        " tiles in some range [x0, x1), [y0, y1). This leaves tiles within rooms"
        " untouched.\n\nA hallway tile is considered a junction if it has at least 3"
        " cardinal neighbors with open terrain.\n\nr0: x0\nr1: y0\nr2: x1\nr3: y1",
    )

    GenerateStandardFloor = Symbol(
        [0x5F08C],
        [0x233BC0C],
        None,
        "Generate a standard floor with the given parameters.\n\nBroadly speaking, a"
        " standard floor is generated as follows:\n1. Generating the grid\n2. Creating"
        " a room or hallway anchor in each grid cell\n3. Creating hallways between grid"
        " cells\n4. Generating special features (maze room, Kecleon shop, Monster"
        " House, extra hallways, room imperfections, secondary structures)\n\nr0: grid"
        " size x\nr1: grid size y\nr2: floor properties",
    )

    GenerateOuterRingFloor = Symbol(
        [0x5F1F4],
        [0x233BD74],
        None,
        "Generates a floor layout with a 4x2 grid of rooms, surrounded by an outer ring"
        " of hallways.\n\nr0: floor properties",
    )

    GenerateCrossroadsFloor = Symbol(
        [0x5F680],
        [0x233C200],
        None,
        "Generates a floor layout with a mesh of hallways on the interior 3x2 grid,"
        " surrounded by a boundary of rooms protruding from the interior like spikes,"
        " excluding the corner cells.\n\nr0: floor properties",
    )

    GenerateLineFloor = Symbol(
        [0x5FAE0],
        [0x233C660],
        None,
        "Generates a floor layout with 5 grid cells in a horizontal line.\n\nr0: floor"
        " properties",
    )

    GenerateCrossFloor = Symbol(
        [0x5FC40],
        [0x233C7C0],
        None,
        "Generates a floor layout with 5 rooms arranged in a cross ('plus sign')"
        " formation.\n\nr0: floor properties",
    )

    GenerateBeetleFloor = Symbol(
        [0x5FDD8],
        [0x233C958],
        None,
        "Generates a floor layout in a 'beetle' formation, which is created by taking a"
        " 3x3 grid of rooms, connecting the rooms within each row, and merging the"
        " central column into one big room.\n\nr0: floor properties",
    )

    MergeRoomsVertically = Symbol(
        [0x5FF94],
        [0x233CB14],
        None,
        "Merges two vertically stacked rooms into one larger room.\n\nr0: x grid"
        " coordinate of the rooms to merge\nr1: y grid coordinate of the upper"
        " room\nr2: dy, where the lower room has a y grid coordinate of y+dy\nr3: grid"
        " to update",
    )

    GenerateOuterRoomsFloor = Symbol(
        [0x600E0],
        [0x233CC60],
        None,
        "Generates a floor layout with a ring of rooms on the grid boundary and nothing"
        " in the interior.\n\nNote that this function is bugged, and won't properly"
        " connect all the rooms together for grid_size_x < 4.\n\nr0: grid size x\nr1:"
        " grid size y\nr2: floor properties",
    )

    IsNotFullFloorFixedRoom = Symbol(
        [0x60374],
        [0x233CEF4],
        None,
        "Checks if a fixed room ID does not correspond to a fixed, full-floor"
        " layout.\n\nThe first non-full-floor fixed room is 0xA5, which is for Sealed"
        " Chambers.\n\nr0: fixed room ID\nreturn: bool",
    )

    GenerateFixedRoom = Symbol(
        [0x60390],
        [0x233CF10],
        None,
        "Handles fixed room generation if the floor contains a fixed room.\n\nr0: fixed"
        " room ID\nr1: floor properties\nreturn: bool",
    )

    GenerateOneRoomMonsterHouseFloor = Symbol(
        [0x607D8],
        [0x233D358],
        None,
        "Generates a floor layout with just a large, one-room Monster House.\n\nThis is"
        " the default layout if dungeon generation fails.\n\nNo params.",
    )

    GenerateTwoRoomsWithMonsterHouseFloor = Symbol(
        [0x608A8],
        [0x233D428],
        None,
        "Generate a floor layout with two rooms (left and right), one of which is a"
        " Monster House.\n\nNo params.",
    )

    GenerateExtraHallways = Symbol(
        [0x60A4C],
        [0x233D5CC],
        None,
        "Generate extra hallways on the floor via a series of random walks.\n\nEach"
        " random walk starts from a random tile in a random room, leaves the room in a"
        " random cardinal direction, and from there tunnels through obstacles through a"
        " series of random turns, leaving open terrain in its wake. The random walk"
        " stops when it reaches open terrain, goes out of bounds, or reaches an"
        " impassable obstruction.\n\nr0: grid to update\nr1: grid size x\nr2: grid size"
        " y\nr3: number of extra hallways to generate",
    )

    GetGridPositions = Symbol(
        [0x60FE8],
        [0x233DB68],
        None,
        "Get the grid cell positions for a given set of floor grid dimensions.\n\nr0:"
        " [output] pointer to array of the starting x coordinates of each grid"
        " column\nr1: [output] pointer to array of the starting y coordinates of each"
        " grid row\nr2: grid size x\nr3: grid size y",
    )

    InitDungeonGrid = Symbol(
        [0x61068],
        [0x233DBE8],
        None,
        "Initialize a dungeon grid with defaults.\n\nThe grid is an array of grid cells"
        " stored in column-major order (such that grid cells with the same x value are"
        " stored contiguously), with a fixed column size of 15. If the grid size in the"
        " y direction is less than this, the last (15 - grid_size_y) entries of each"
        " column will be uninitialized.\n\nNote that the grid size arguments define the"
        " maximum size of the grid from a programmatic standpoint. However, grid cells"
        " can be invalidated if they exceed the configured floor size in the dungeon"
        " generation status struct. Thus, the dimensions of the ACTIVE grid can be"
        " smaller.\n\nr0: [output] grid (expected to have space for at least"
        " (15*(grid_size_x-1) + grid_size_y) dungeon grid cells)\nr1: grid size x\nr2:"
        " grid size y",
    )

    AssignRooms = Symbol(
        [0x61168],
        [0x233DCE8],
        None,
        "Randomly selects a subset of grid cells to become rooms.\n\nThe given number"
        " of grid cells will become rooms. If any of the selected grid cells are"
        " invalid, fewer rooms will be generated. The number of rooms assigned will"
        " always be at least 2 and never exceed 36.\n\nCells not marked as rooms will"
        " become hallway anchors. A hallway anchor is a single tile in a non-room grid"
        " cell to which hallways will be connected later, thus 'anchoring' hallway"
        " generation.\n\nr0: grid to update\nr1: grid size x\nr2: grid size y\nr3:"
        " number of rooms; if positive, a random value between [n_rooms, n_rooms+2]"
        " will be used. If negative, |n_rooms| will be used exactly.",
    )

    CreateRoomsAndAnchors = Symbol(
        [0x6137C],
        [0x233DEFC],
        None,
        "Creates rooms and hallway anchors in each grid cell as designated by"
        " AssignRooms.\n\nThis function creates a rectangle of open terrain for each"
        " room (with some margin relative to the grid cell border). A single open tile"
        " is created in hallway anchor cells, and a hallway anchor indicator is set for"
        " later reference.\n\nr0: grid to update\nr1: grid size x\nr2: grid size y\nr3:"
        " array of the starting x coordinates of each grid column\nstack[0]: array of"
        " the starting y coordinates of each grid row\nstack[1]: room bitflags; only"
        " uses bit 2 (mask: 0b100), which enables room imperfections",
    )

    GenerateSecondaryStructures = Symbol(
        [0x616D8],
        [0x233E258],
        None,
        "Try to generate secondary structures in flagged rooms.\n\nIf a valid room with"
        " no special features is flagged to have a secondary structure, try to generate"
        " a random one in the room, based on the result of a dice roll:\n  0: no"
        " secondary structure\n  1: maze, or a central water/lava 'plus sign' as"
        " fallback, or a single water/lava tile in the center as a second fallback\n "
        " 2: checkerboard pattern of water/lava\n  3: central pool of water/lava\n  4:"
        " central 'island' with items and a Warp Tile, surrounded by a 'moat' of"
        " water/lava\n  5: horizontal or vertical divider of water/lava splitting the"
        " room in two\n\nIf the room isn't the right shape, dimension, or otherwise"
        " doesn't support the selected secondary structure, it is left"
        " untouched.\n\nr0: grid to update\nr1: grid size x\nr2: grid size y",
    )

    AssignGridCellConnections = Symbol(
        [0x620C0],
        [0x233EC40],
        None,
        "Randomly assigns connections between adjacent grid cells.\n\nConnections are"
        " created via a random walk with momentum, starting from the grid cell at"
        " (cursor x, cursor y). A connection is drawn in a random direction from the"
        " current cursor, and this process is repeated a certain number of times (the"
        " 'floor connectivity' specified in the floor properties). The direction of the"
        " random walk has 'momentum'; there's a 50% chance it will be the same as the"
        " previous step (or rotated counterclockwise if on the boundary). This helps to"
        " reduce the number of dead ends and forks in the road caused by the random"
        " walk 'doubling back' on itself.\n\nIf dead ends are disabled in the floor"
        " properties, there is an additional phase to remove dead end hallway anchors"
        " (only hallway anchors, not rooms) by drawing additional connections. Note"
        " that the actual implementation contains a bug: the grid cell validity checks"
        " use the wrong index, so connections may be drawn to invalid cells.\n\nr0:"
        " grid to update\nr1: grid size x\nr2: grid size y\nr3: cursor x\nstack[0]:"
        " cursor y\nstack[1]: floor properties",
    )

    CreateGridCellConnections = Symbol(
        [0x624A0],
        [0x233F020],
        None,
        "Create grid cell connections either by creating hallways or merging"
        " rooms.\n\nWhen creating a hallway connecting a hallway anchor, the exact"
        " anchor coordinates are used as the endpoint. When creating a hallway"
        " connecting a room, a random point on the room edge facing the hallway is used"
        " as the endpoint. The grid cell boundaries are used as the middle coordinates"
        " for kinks (see CreateHallway).\n\nIf room merging is enabled, there is a"
        " 9.75% chance that two connected rooms will be merged into a single larger"
        " room (9.75% comes from two 5% rolls, one for each of the two rooms being"
        " merged). A room can only participate in a merge once.\n\nr0: grid to"
        " update\nr1: grid size x\nr2: grid size y\nr3: array of the starting x"
        " coordinates of each grid column\nstack[0]: array of the starting y"
        " coordinates of each grid row\nstack[1]: disable room merging flag",
    )

    GenerateRoomImperfections = Symbol(
        [0x62D98],
        [0x233F918],
        None,
        "Attempt to generate room imperfections for each room in the floor layout, if"
        " enabled.\n\nEach room has a 40% chance of having imperfections if its grid"
        " cell is flagged to allow room imperfections. Imperfections are generated by"
        " randomly growing the walls of the room inwards for a certain number of"
        " iterations, starting from the corners.\n\nr0: grid to update\nr1: grid size"
        " x\nr2: grid size y",
    )

    CreateHallway = Symbol(
        [0x63184],
        [0x233FD04],
        None,
        "Create a hallway between two points.\n\nIf the two points share no coordinates"
        " in common (meaning the line connecting them is diagonal), a 'kinked' hallway"
        " is created, with the kink at a specified 'middle' coordinate (in practice the"
        " grid cell boundary). For example, with a kinked horizontal hallway, there are"
        " two horizontal lines extending out from the endpoints, connected by a"
        " vertical line on the middle x coordinate.\n\nIf a hallway would intersect"
        " with an existing open tile (like an existing hallway), the hallway will only"
        " be created up to the point where it intersects with the open tile.\n\nr0:"
        " x0\nr1: y0\nr2: x1\nr3: y1\nstack[0]: vertical flag (true for vertical"
        " hallway, false for horizontal)\nstack[1]: middle x coordinate for kinked"
        " horizontal hallways\nstack[2]: middle y coordinate for kinked vertical"
        " hallways",
    )

    EnsureConnectedGrid = Symbol(
        [0x63488],
        [0x2340008],
        None,
        "Ensure the grid forms a connected graph (all valid cells are reachable) by"
        " adding hallways to unreachable grid cells.\n\nIf a grid cell cannot be"
        " connected for some reason, remove it entirely.\n\nr0: grid to update\nr1:"
        " grid size x\nr2: grid size y\nr3: array of the starting x coordinates of each"
        " grid column\nstack[0]: array of the starting y coordinates of each grid row",
    )

    SetTerrainObstacleChecked = Symbol(
        [0x63964],
        [0x23404E4],
        None,
        "Set the terrain of a specific tile to be an obstacle (wall or secondary"
        " terrain).\n\nSecondary terrain (water/lava) can only be placed in the"
        " specified room. If the tile room index does not match, a wall will be placed"
        " instead.\n\nr0: tile pointer\nr1: use secondary terrain flag (true for"
        " water/lava, false for wall)\nr2: room index",
    )

    FinalizeJunctions = Symbol(
        [0x639A0],
        [0x2340520],
        None,
        "Finalizes junction tiles by setting the junction flag (bit 3 of the terrain"
        " flags) and ensuring open terrain.\n\nNote that this implementation is"
        " slightly buggy. This function scans tiles left-to-right, top-to-bottom, and"
        " identifies junctions as any open, non-hallway tile (room_index != 0xFF)"
        " adjacent to an open, hallway tile (room_index == 0xFF). This interacts poorly"
        " with hallway anchors (room_index == 0xFE). This function sets the room index"
        " of any hallway anchors to 0xFF within the same loop, so a hallway anchor may"
        " or may not be identified as a junction depending on the orientation of"
        " connected hallways.\n\nFor example, in the following configuration, the 'o'"
        " tile would be marked as a junction because the neighboring hallway tile to"
        " its left comes earlier in iteration, while the 'o' tile still has the room"
        " index 0xFE, causing the algorithm to mistake it for a room tile:\n  xxxxx\n "
        " ---ox\n  xxx|x\n  xxx|x\nHowever, in the following configuration, the 'o'"
        " tile would NOT be marked as a junction because it comes earlier in iteration"
        " than any of its neighboring hallway tiles, so its room index is set to 0xFF"
        " before it can be marked as a junction. This is actually the ONLY possible"
        " configuration where a hallway anchor will not be marked as a junction.\n "
        " xxxxx\n  xo---\n  x|xxx\n  x|xxx\n\nNo params.",
    )

    GenerateKecleonShop = Symbol(
        [0x63C4C],
        [0x23407CC],
        None,
        "Possibly generate a Kecleon shop on the floor.\n\nA Kecleon shop will be"
        " generated with a probability determined by the Kecleon shop spawn chance"
        " parameter. A Kecleon shop will be generated in a random room that is valid,"
        " connected, has no other special features, and has dimensions of at least 5x4."
        " Kecleon shops will occupy the entire room interior, leaving a one tile margin"
        " from the room walls.\n\nr0: grid to update\nr1: grid size x\nr2: grid size"
        " y\nr3: Kecleon shop spawn chance (percentage from 0-100)",
    )

    GenerateMonsterHouse = Symbol(
        [0x64000],
        [0x2340B80],
        None,
        "Possibly generate a Monster House on the floor.\n\nA Monster House will be"
        " generated with a probability determined by the Monster House spawn chance"
        " parameter, and only if the current floor can support one (no"
        " non-Monster-House outlaw missions or special floor types). A Monster House"
        " will be generated in a random room that is valid, connected, and is not a"
        " merged or maze room.\n\nr0: grid to update\nr1: grid size x\nr2: grid size"
        " y\nr3: Monster House spawn chance (percentage from 0-100)",
    )

    GenerateMazeRoom = Symbol(
        [0x64288],
        [0x2340E08],
        None,
        "Possibly generate a maze room on the floor.\n\nA maze room will be generated"
        " with a probability determined by the maze room chance parameter. A maze will"
        " be generated in a random room that is valid, connected, has odd dimensions,"
        " and has no other features.\n\nr0: grid to update\nr1: grid size x\nr2: grid"
        " size y\nr3: maze room chance (percentage from 0-100)",
    )

    GenerateMaze = Symbol(
        [0x644BC],
        [0x234103C],
        None,
        "Generate a maze room within a given grid cell.\n\nA 'maze' is generated within"
        " the room using a series of random walks to place obstacle terrain (walls or"
        " secondary terrain) in a maze-like arrangement. 'Maze lines' (see"
        " GenerateMazeLine) are generated using every other tile around the room's"
        " border, as well as every other interior tile, as a starting point. This"
        " ensures that there are stripes of walkable open terrain surrounded by stripes"
        " of obstacles (the maze walls).\n\nr0: grid cell pointer\nr1: use secondary"
        " terrain flag (true for water/lava, false for walls)",
    )

    GenerateMazeLine = Symbol(
        [0x64738],
        [0x23412B8],
        None,
        "Generate a 'maze line' from a given starting point, within the given"
        " bounds.\n\nA 'maze line' is a random walk starting from (x0, y0). The random"
        " walk proceeds with a stride of 2 in a random direction, laying down obstacles"
        " as it goes. The random walk terminates when it gets trapped and there are no"
        " more neighboring tiles that are open and in-bounds.\n\nr0: x0\nr1: y0\nr2:"
        " xmin\nr3: ymin\nstack[0]: xmax\nstack[1]: ymax\nstack[2]: use secondary"
        " terrain flag (true for water/lava, false for walls)\nstack[3]: room index",
    )

    SetSpawnFlag5 = Symbol(
        [0x648E0],
        [0x2341460],
        None,
        "Set spawn flag 5 (0b100000 or 0x20) on all tiles in a room.\n\nr0: grid cell",
    )

    IsNextToHallway = Symbol(
        [0x64934],
        [0x23414B4],
        None,
        "Checks if a tile position is either in a hallway or next to one.\n\nr0: x\nr1:"
        " y\nreturn: bool",
    )

    ResolveInvalidSpawns = Symbol(
        [0x649D8],
        [0x2341558],
        None,
        "Resolve invalid spawn flags on tiles.\n\nSpawn flags can be invalid due to"
        " terrain. For example, traps can't spawn on obstacles. Spawn flags can also be"
        " invalid due to multiple being set on a single tile, in which case one will"
        " take precedence. For example, stair spawns trump trap spawns.\n\nNo params.",
    )

    ConvertSecondaryTerrainToChasms = Symbol(
        [0x64A70],
        [0x23415F0],
        None,
        "Converts all secondary terrain tiles (water/lava) to chasms.\n\nNo params.",
    )

    EnsureImpassableTilesAreWalls = Symbol(
        [0x64ADC],
        [0x234165C],
        None,
        "Ensures all tiles with the impassable flag are walls.\n\nNo params.",
    )

    InitializeTile = Symbol(
        [0x64B38], [0x23416B8], None, "Initialize a tile struct.\n\nr0: tile pointer"
    )

    ResetFloor = Symbol(
        [0x64B70],
        [0x23416F0],
        None,
        "Resets the floor in preparation for a floor generation attempt.\n\nResets all"
        " tiles, resets the border to be impassable, and clears entity spawns.\n\nNo"
        " params.",
    )

    PosIsOutOfBounds = Symbol(
        [0x64D10],
        [0x2341890],
        None,
        "Checks if a position (x, y) is out of bounds on the map: !((0 <= x <= 55) &&"
        " (0 <= y <= 31)).\n\nr0: x\nr1: y\nreturn: bool",
    )

    ShuffleSpawnPositions = Symbol(
        [0x64D48],
        [0x23418C8],
        None,
        "Randomly shuffle an array of spawn positions.\n\nr0: spawn position array"
        " containing bytes {x1, y1, x2, y2, ...}\nr1: number of (x, y) pairs in the"
        " spawn position array",
    )

    SpawnNonEnemies = Symbol(
        [0x64DB0],
        [0x2341930],
        None,
        "Spawn all non-enemy entities, which includes stairs, items, traps, and the"
        " player.\n\nMost entities are spawned randomly on a subset of permissible"
        " tiles.\n\nStairs are spawned if they don't already exist on the floor, and"
        " hidden stairs of the specified type are also spawned if configured as long as"
        " there are at least 2 floors left in the dungeon. Stairs can spawn on any tile"
        " that has open terrain, is in a room, isn't in a Kecleon shop, doesn't already"
        " have an enemy spawn, isn't a hallway junction, and isn't a special tile like"
        " a Key door.\n\nItems are spawned both normally in rooms, as well as in walls"
        " and Monster Houses. Normal items can spawn on any tile that has open terrain,"
        " is in a room, isn't in a Kecleon shop or Monster House, isn't a hallway"
        " junction, and isn't a special tile like a Key door. Buried items can spawn on"
        " any wall tile. Monster House items can spawn on any Monster House tile that"
        " isn't in a Kecleon shop and isn't a hallway junction.\n\nTraps are similarly"
        " spawned both normally in rooms, as well as in Monster Houses. Normal traps"
        " can spawn on any tile that has open terrain, is in a room, isn't in a Kecleon"
        " shop, doesn't already have an item or enemy spawn, and isn't a special tile"
        " like a Key door. Monster House traps follow the same conditions as Monster"
        " House items.\n\nThe player can spawn on any tile that has open terrain, is in"
        " a room, isn't in a Kecleon shop, isn't a hallway junction, doesn't already"
        " have an item, enemy, or trap spawn, and isn't a special tile like a Key"
        " door.\n\nr0: floor properties\nr1: empty Monster House flag. An empty Monster"
        " House is one with no items or traps, and only a small number of enemies.",
    )

    SpawnEnemies = Symbol(
        [0x654D4],
        [0x2342054],
        None,
        "Spawn all enemies, which includes normal enemies and those in Monster"
        " Houses.\n\nNormal enemies can spawn on any tile that has open terrain, isn't"
        " in a Kecleon shop, doesn't already have another entity spawn, and isn't a"
        " special tile like a Key door.\n\nMonster House enemies can spawn on any"
        " Monster House tile that isn't in a Kecleon shop, isn't where the player"
        " spawns, and isn't a special tile like a Key door.\n\nr0: floor"
        " properties\nr1: empty Monster House flag. An empty Monster House is one with"
        " no items or traps, and only a small number of enemies.",
    )

    SetSecondaryTerrainOnWall = Symbol(
        [0x657D0],
        [0x2342350],
        None,
        "Set a specific tile to have secondary terrain (water/lava), but only if it's a"
        " passable wall.\n\nr0: tile pointer",
    )

    GenerateSecondaryTerrainFormations = Symbol(
        [0x65810],
        [0x2342390],
        None,
        "Generate secondary terrain (water/lava) formations.\n\nThis includes 'rivers'"
        " that flow from top-to-bottom (or bottom-to-top), as well as 'lakes' both"
        " standalone and after rivers. Water/lava formations will never cut through"
        " rooms, but they can pass through rooms to the opposite side.\n\nRivers are"
        " generated by a top-down or bottom-up random walk that ends when existing"
        " secondary terrain is reached or the walk goes out of bounds. Some rivers also"
        " end prematurely in a lake. Lakes are a large collection of secondary terrain"
        " generated around a central point.\n\nr0: bit index to test in the floor"
        " properties room flag bitvector (formations are only generated if the bit is"
        " set)\nr1: floor properties",
    )

    StairsAlwaysReachable = Symbol(
        [0x65ED0],
        [0x2342A50],
        None,
        "Checks that the stairs are reachable from every walkable tile on the"
        " floor.\n\nThis runs a graph traversal algorithm that is very similar to"
        " breadth-first search (the order in which nodes are visited is slightly"
        " different), starting from the stairs. If any tile is walkable but wasn't"
        " reached by the traversal algorithm, then the stairs must not be reachable"
        " from that tile.\n\nr0: x coordinate of the stairs\nr1: y coordinate of the"
        " stairs\nr2: flag to always return true, but set a special bit on all walkable"
        " tiles that aren't reachable from the stairs\nreturn: bool",
    )

    ConvertWallsToChasms = Symbol(
        [0x665AC], [0x234312C], None, "Converts all wall tiles to chasms.\n\nNo params."
    )

    ResetInnerBoundaryTileRows = Symbol(
        [0x66BE0],
        [0x2343760],
        None,
        "Reset the inner boundary tile rows (y == 1 and y == 30) to their initial state"
        " of all wall tiles, with impassable walls at the edges (x == 0 and x =="
        " 55).\n\nNo params.",
    )

    SpawnStairs = Symbol(
        [0x66CF0],
        [0x2343870],
        None,
        "Spawn stairs at the given location.\n\nIf the hidden stairs flag is set,"
        " hidden stairs will be spawned instead of normal stairs.\n\nIf spawning normal"
        " stairs and the current floor is a rescue floor, the room containing the"
        " stairs will be converted into a Monster House.\n\nr0: position (two-byte"
        " array for {x, y})\nr1: dungeon generation info pointer (a field on the"
        " dungeon struct)\nr2: hidden stairs flag",
    )

    LoadFixedRoomData = Symbol(
        [0x67DF4],
        [0x2344974],
        None,
        "Loads fixed room data from BALANCE/fixed.bin into the buffer pointed to by"
        " FIXED_ROOM_DATA_PTR.\n\nNo params.",
    )

    IsHiddenStairsFloor = Symbol(
        [0x68570],
        [0x23450F0],
        None,
        "Checks if the current floor is either the Secret Bazaar or a Secret"
        " Room.\n\nreturn: bool",
    )

    HasHeldItem = Symbol(
        [0x6A850],
        [0x23473D0],
        None,
        "Checks if a monster has a certain held item.\n\nr0: entity pointer\nr1: item"
        " ID\nreturn: bool",
    )

    IsOutlawOrChallengeRequestFloor = Symbol(
        [0x6D244],
        [0x2349DC4],
        None,
        "Checks if the current floor is an active mission destination of type"
        " MISSION_TAKE_ITEM_FROM_OUTLAW, MISSION_ARREST_OUTLAW or"
        " MISSION_CHALLENGE_REQUEST.\n\nreturn: bool",
    )

    IsCurrentMissionType = Symbol(
        [0x6D29C],
        [0x2349E1C],
        None,
        "Checks if the current floor is an active mission destination of a given type"
        " (and any subtype).\n\nr0: mission type\nreturn: bool",
    )

    IsCurrentMissionTypeExact = Symbol(
        [0x6D2D0],
        [0x2349E50],
        None,
        "Checks if the current floor is an active mission destination of a given type"
        " and subtype.\n\nr0: mission type\nr1: mission subtype\nreturn: bool",
    )

    IsOutlawMonsterHouseFloor = Symbol(
        [0x6D30C],
        [0x2349E8C],
        None,
        "Checks if the current floor is a mission destination for a Monster House"
        " outlaw mission.\n\nreturn: bool",
    )

    IsGoldenChamber = Symbol(
        [0x6D330],
        [0x2349EB0],
        None,
        "Checks if the current floor is a Golden Chamber floor.\n\nreturn: bool",
    )

    IsLegendaryChallengeFloor = Symbol(
        [0x6D354],
        [0x2349ED4],
        None,
        "Checks if the current floor is a boss floor for a Legendary Challenge Letter"
        " mission.\n\nreturn: bool",
    )

    IsJirachiChallengeFloor = Symbol(
        [0x6D394],
        [0x2349F14],
        None,
        "Checks if the current floor is the boss floor in Star Cave Pit for Jirachi's"
        " Challenge Letter mission.\n\nreturn: bool",
    )

    IsDestinationFloorWithMonster = Symbol(
        [0x6D3CC],
        [0x2349F4C],
        None,
        "Checks if the current floor is a mission destination floor with a special"
        " monster.\n\nSee FloorHasMissionMonster for details.\n\nreturn: bool",
    )

    LoadMissionMonsterSprites = Symbol(
        [0x6D478],
        [0x2349FF8],
        None,
        "Loads the sprites of monsters that appear on the current floor because of a"
        " mission, if applicable.\n\nThis includes monsters to be rescued, outlaws and"
        " its minions.\n\nNo params.",
    )

    MissionTargetEnemyIsDefeated = Symbol(
        [0x6D4F0],
        [0x234A070],
        None,
        "Checks if the target enemy of the mission on the current floor has been"
        " defeated.\n\nreturn: bool",
    )

    SetMissionTargetEnemyDefeated = Symbol(
        [0x6D510],
        [0x234A090],
        None,
        "Set the flag for whether or not the target enemy of the current mission has"
        " been defeated.\n\nr0: new flag value",
    )

    IsDestinationFloorWithFixedRoom = Symbol(
        [0x6D524],
        [0x234A0A4],
        None,
        "Checks if the current floor is a mission destination floor with a fixed"
        " room.\n\nThe entire floor can be a fixed room layout, or it can just contain"
        " a Sealed Chamber.\n\nreturn: bool",
    )

    GetItemToRetrieve = Symbol(
        [0x6D54C],
        [0x234A0CC],
        None,
        "Get the ID of the item that needs to be retrieve on the current floor for a"
        " mission, if one exists.\n\nreturn: item ID",
    )

    GetItemToDeliver = Symbol(
        [0x6D570],
        [0x234A0F0],
        None,
        "Get the ID of the item that needs to be delivered to a mission client on the"
        " current floor, if one exists.\n\nreturn: item ID",
    )

    GetSpecialTargetItem = Symbol(
        [0x6D59C],
        [0x234A11C],
        None,
        "Get the ID of the special target item for a Sealed Chamber or Treasure Memo"
        " mission on the current floor.\n\nreturn: item ID",
    )

    IsDestinationFloorWithItem = Symbol(
        [0x6D5E4],
        [0x234A164],
        None,
        "Checks if the current floor is a mission destination floor with a special"
        " item.\n\nThis excludes missions involving taking an item from an"
        " outlaw.\n\nreturn: bool",
    )

    IsDestinationFloorWithHiddenOutlaw = Symbol(
        [0x6D644],
        [0x234A1C4],
        None,
        "Checks if the current floor is a mission destination floor with a 'hidden"
        " outlaw' that behaves like a normal enemy.\n\nreturn: bool",
    )

    IsDestinationFloorWithFleeingOutlaw = Symbol(
        [0x6D668],
        [0x234A1E8],
        None,
        "Checks if the current floor is a mission destination floor with a 'fleeing"
        " outlaw' that runs away.\n\nreturn: bool",
    )

    GetMissionTargetEnemy = Symbol(
        [0x6D6A0],
        [0x234A220],
        None,
        "Get the monster ID of the target enemy to be defeated on the current floor for"
        " a mission, if one exists.\n\nreturn: monster ID",
    )

    GetMissionEnemyMinionGroup = Symbol(
        [0x6D6B8],
        [0x234A238],
        None,
        "Get the monster ID of the specified minion group on the current floor for a"
        " mission, if it exists.\n\nNote that a single minion group can correspond to"
        " multiple actual minions of the same species. There can be up to 2 minion"
        " groups.\n\nr0: minion group index (0-indexed)\nreturn: monster ID",
    )

    SetTargetMonsterNotFoundFlag = Symbol(
        [0x6D744],
        [0x234A2C4],
        None,
        "Sets dungeon::target_monster_not_found_flag to the specified value.\n\nr0:"
        " Value to set the flag to",
    )

    GetTargetMonsterNotFoundFlag = Symbol(
        [0x6D758],
        [0x234A2D8],
        None,
        "Gets the value of dungeon::target_monster_not_found_flag.\n\nreturn:"
        " dungeon::target_monster_not_found_flag",
    )

    FloorHasMissionMonster = Symbol(
        [0x6D7C8],
        [0x234A348],
        None,
        "Checks if a given floor is a mission destination with a special monster,"
        " either a target to rescue or an enemy to defeat.\n\nMission types with a"
        " monster on the destination floor:\n- Rescue client\n- Rescue target\n- Escort"
        " to target\n- Deliver item\n- Search for target\n- Take item from outlaw\n-"
        " Arrest outlaw\n- Challenge Request\n\nr0: mission destination info"
        " pointer\nreturn: bool",
    )

    LogMessageByIdWithPopupCheckUser = Symbol(
        [0x6F324],
        [0x234BEA4],
        None,
        "Logs a message in the message log alongside a message popup, if the user"
        " hasn't fainted.\n\nr0: user entity pointer\nr1: message ID",
    )

    LogMessageWithPopupCheckUser = Symbol(
        [0x6F364],
        [0x234BEE4],
        None,
        "Logs a message in the message log alongside a message popup, if the user"
        " hasn't fainted.\n\nr0: user entity pointer\nr1: message string",
    )

    LogMessageByIdQuiet = Symbol(
        [0x6F39C],
        [0x234BF1C],
        None,
        "Logs a message in the message log (but without a message popup).\n\nr0: user"
        " entity pointer\nr1: message ID",
    )

    LogMessageQuiet = Symbol(
        [0x6F3C0],
        [0x234BF40],
        None,
        "Logs a message in the message log (but without a message popup).\n\nr0: user"
        " entity pointer\nr1: message string",
    )

    LogMessageByIdWithPopupCheckUserTarget = Symbol(
        [0x6F3D0],
        [0x234BF50],
        None,
        "Logs a message in the message log alongside a message popup, if some user"
        " check passes and the target hasn't fainted.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: message ID",
    )

    LogMessageWithPopupCheckUserTarget = Symbol(
        [0x6F424],
        [0x234BFA4],
        None,
        "Logs a message in the message log alongside a message popup, if some user"
        " check passes and the target hasn't fainted.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: message string",
    )

    LogMessageByIdQuietCheckUserTarget = Symbol(
        [0x6F470],
        [0x234BFF0],
        None,
        "Logs a message in the message log (but without a message popup), if some user"
        " check passes and the target hasn't fainted.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: message ID",
    )

    LogMessageByIdWithPopupCheckUserUnknown = Symbol(
        [0x6F4C4],
        [0x234C044],
        None,
        "Logs a message in the message log alongside a message popup, if the user"
        " hasn't fainted and some other unknown check.\n\nr0: user entity pointer\nr1:"
        " ?\nr2: message ID",
    )

    LogMessageByIdWithPopup = Symbol(
        [0x6F518],
        [0x234C098],
        None,
        "Logs a message in the message log alongside a message popup.\n\nr0: user"
        " entity pointer\nr1: message ID",
    )

    LogMessageWithPopup = Symbol(
        [0x6F53C],
        [0x234C0BC],
        None,
        "Logs a message in the message log alongside a message popup.\n\nr0: user"
        " entity pointer\nr1: message string",
    )

    LogMessage = Symbol(
        [0x6F588],
        [0x234C108],
        None,
        "Logs a message in the message log.\n\nr0: user entity pointer\nr1: message"
        " string\nr2: bool, whether or not to present a message popup",
    )

    LogMessageById = Symbol(
        [0x6F794],
        [0x234C314],
        None,
        "Logs a message in the message log.\n\nr0: user entity pointer\nr1: message"
        " ID\nr2: bool, whether or not to present a message popup",
    )

    OpenMessageLog = Symbol(
        [0x6FBDC], [0x234C75C], None, "Opens the message log window.\n\nr0: ?\nr1: ?"
    )

    RunDungeonMode = Symbol(
        [0x6FFA8],
        [0x234CB28],
        None,
        "This appears to be the top-level function for running dungeon mode.\n\nIt gets"
        " called by some code in overlay 10 right after doing the dungeon fade"
        " transition, and once it exits, the dungeon results are processed.\n\nThis"
        " function is presumably in charge of allocating the dungeon struct, setting it"
        " up, launching the dungeon engine, etc.",
    )

    DisplayDungeonTip = Symbol(
        [0x70F70],
        [0x234DAF0],
        None,
        "Checks if a given dungeon tip should be displayed at the start of a floor and"
        " if so, displays it. Called up to 4 times at the start of each new floor, with"
        " a different r0 parameter each time.\n\nr0: Pointer to the message_tip struct"
        " of the message that should be displayed\nr1: True to log the message in the"
        " message log",
    )

    SetBothScreensWindowColorToDefault = Symbol(
        [0x70FE0],
        [0x234DB60],
        None,
        "This changes the palettes of windows in both screens to an appropiate value"
        " depending on the playthrough\nIf you're in a special episode, they turn green"
        " , otherwise, they turn blue or pink depending on your character's sex\n\nNo"
        " params",
    )

    DisplayMessage = Symbol(
        [0x712D8],
        [0x234DE58],
        None,
        "Displays a message in a dialogue box that optionally waits for player input"
        " before closing.\n\nr0: ?\nr1: ID of the string to display\nr2: True to wait"
        " for player input before closing the dialogue box, false to close it"
        " automatically once all the characters get printed.",
    )

    DisplayMessage2 = Symbol(
        [0x7132C], [0x234DEAC], None, "Very similar to DisplayMessage"
    )

    DisplayMessageInternal = Symbol(
        [0x71610],
        [0x234E190],
        None,
        "Called by DisplayMessage. Seems to be the function that handles the display of"
        " the dialogue box. It won't return until all the characters have been written"
        " and after the player manually closes the dialogue box (if the corresponding"
        " parameter was set).\n\nr0: ID of the string to display\nr1: True to wait for"
        " player input before closing the dialogue box, false to close it automatically"
        " once all the characters get printed.\nr2: ? (r0 in DisplayMessage)\nr3:"
        " ?\nstack[0]: ?\nstack[1]: ?",
    )


class EuOverlay29Data:
    DUNGEON_STRUCT_SIZE = Symbol(
        [0x2838, 0x286C],
        [0x22DF3B8, 0x22DF3EC],
        0x4,
        "Size of the dungeon struct (0x2CB14)",
    )

    MAX_HP_CAP = Symbol(
        [0x7C00, 0x356F4, 0x3C334],
        [0x22E4780, 0x2312274, 0x2318EB4],
        0x4,
        "The maximum amount of HP a monster can have (999).",
    )

    OFFSET_OF_DUNGEON_FLOOR_PROPERTIES = Symbol(
        [0xB828, 0x5EECC],
        [0x22E83A8, 0x233BA4C],
        0x4,
        "Offset of the floor properties field in the dungeon struct (0x286B2)",
    )

    SPAWN_RAND_MAX = Symbol(
        [0xBC80],
        [0x22E8800],
        0x4,
        "Equal to 10,000 (0x2710). Used as parameter for DungeonRandInt to generate the"
        " random number which determines the entity to spawn.",
    )

    DUNGEON_PRNG_LCG_MULTIPLIER = Symbol(
        [0xE7F8, 0xE8BC],
        [0x22EB378, 0x22EB43C],
        0x4,
        "The multiplier shared by all of the dungeon PRNG's LCGs, 1566083941"
        " (0x5D588B65).",
    )

    DUNGEON_PRNG_LCG_INCREMENT_SECONDARY = Symbol(
        [0xE8C4],
        [0x22EB444],
        0x4,
        "The increment for the dungeon PRNG's secondary LCGs, 2531011 (0x269EC3). This"
        " happens to be the same increment that the Microsoft Visual C++ runtime"
        " library uses in its implementation of the rand() function.",
    )

    KECLEON_FEMALE_ID = Symbol(
        [0x1B23C],
        [0x22F7DBC],
        0x4,
        "0x3D7 (983). Used when spawning Kecleon on an even numbered floor.",
    )

    KECLEON_MALE_ID = Symbol(
        [0x1B240],
        [0x22F7DC0],
        0x4,
        "0x17F (383). Used when spawning Kecleon on an odd numbered floor.",
    )

    MSG_ID_SLOW_START = Symbol(
        [0x1D15C],
        [0x22F9CDC],
        0x4,
        "ID of the message printed when a monster has the ability Slow Start at the"
        " beginning of the floor.",
    )

    EXPERIENCE_POINT_GAIN_CAP = Symbol(
        [0x26574],
        [0x23030F4],
        0x4,
        "A cap on the experience that can be given to a monster in one call to"
        " AddExpSpecial",
    )

    JUDGMENT_MOVE_ID = Symbol(
        [0x3034C],
        [0x230CECC],
        0x4,
        "Move ID for Judgment (0x1D3)\n\ntype: enum move_id",
    )

    REGULAR_ATTACK_MOVE_ID = Symbol(
        [0x30350],
        [0x230CED0],
        0x4,
        "Move ID for the regular attack (0x163)\n\ntype: enum move_id",
    )

    DEOXYS_ATTACK_ID = Symbol(
        [0x30354],
        [0x230CED4],
        0x4,
        "Monster ID for Deoxys in Attack Forme (0x1A3)\n\ntype: enum monster_id",
    )

    DEOXYS_SPEED_ID = Symbol(
        [0x30358],
        [0x230CED8],
        0x4,
        "Monster ID for Deoxys in Speed Forme (0x1A5)\n\ntype: enum monster_id",
    )

    GIRATINA_ALTERED_ID = Symbol(
        [0x3035C],
        [0x230CEDC],
        0x4,
        "Monster ID for Giratina in Altered Forme (0x211)\n\ntype: enum monster_id",
    )

    PUNISHMENT_MOVE_ID = Symbol(
        [0x30360],
        [0x230CEE0],
        0x4,
        "Move ID for Punishment (0x1BD)\n\ntype: enum move_id",
    )

    OFFENSE_STAT_MAX = Symbol(
        [0x30390],
        [0x230CF10],
        0x4,
        "Cap on an attacker's modified offense (attack or special attack) stat after"
        " boosts. Used during damage calculation.",
    )

    PROJECTILE_MOVE_ID = Symbol(
        [0x30F70, 0x405E0],
        [0x230DAF0, 0x231D160],
        0x4,
        "The move ID of the special 'projectile' move (0x195)\n\ntype: enum move_id",
    )

    BELLY_LOST_PER_TURN = Symbol(
        [0x34950],
        [0x23114D0],
        0x4,
        "The base value by which belly is decreased every turn.\n\nIts raw value is"
        " 0x199A, which encodes a binary fixed-point number (16 fraction bits) with"
        " value (0x199A * 2^-16), and is the closest approximation to 0.1 representable"
        " in this number format.",
    )

    MOVE_TARGET_AND_RANGE_SPECIAL_USER_HEALING = Symbol(
        [0x3EC14],
        [0x231B794],
        0x4,
        "The move target and range code for special healing moves that target just the"
        " user (0x273).\n\ntype: struct move_target_and_range (+ padding)",
    )

    PLAIN_SEED_VALUE = Symbol(
        [0x40628], [0x231D1A8], 0x4, "Some value related to the Plain Seed (0xBE9)."
    )

    MAX_ELIXIR_PP_RESTORATION = Symbol(
        [0x4062C],
        [0x231D1AC],
        0x4,
        "The amount of PP restored per move by ingesting a Max Elixir (0x3E7).",
    )

    SLIP_SEED_VALUE = Symbol(
        [0x40A94], [0x231D614], 0x4, "Some value related to the Slip Seed (0xC75)."
    )

    CASTFORM_NORMAL_FORM_MALE_ID = Symbol(
        [0x592F8], [0x2335E78], 0x4, "Castform's male normal form ID (0x17B)"
    )

    CASTFORM_NORMAL_FORM_FEMALE_ID = Symbol(
        [0x592FC], [0x2335E7C], 0x4, "Castform's female normal form ID (0x3D3)"
    )

    CHERRIM_SUNSHINE_FORM_MALE_ID = Symbol(
        [0x59300], [0x2335E80], 0x4, "Cherrim's male sunshine form ID (0x1CD)"
    )

    CHERRIM_OVERCAST_FORM_FEMALE_ID = Symbol(
        [0x59304], [0x2335E84], 0x4, "Cherrim's female overcast form ID (0x424)"
    )

    CHERRIM_SUNSHINE_FORM_FEMALE_ID = Symbol(
        [0x59308], [0x2335E88], 0x4, "Cherrim's female sunshine form ID (0x425)"
    )

    FLOOR_GENERATION_STATUS_PTR = Symbol(
        [
            0x5EED0,
            0x5EF6C,
            0x5F1F0,
            0x5F67C,
            0x5FADC,
            0x5FC3C,
            0x5FDD4,
            0x5FF90,
            0x60370,
            0x607D0,
            0x60FE4,
            0x61164,
            0x61374,
            0x616D4,
            0x620BC,
            0x63FF4,
            0x64280,
            0x64734,
            0x654C0,
            0x657C8,
            0x661DC,
            0x66574,
            0x66844,
            0x66BD8,
            0x66CC8,
            0x66DFC,
            0x66F8C,
        ],
        [
            0x233BA50,
            0x233BAEC,
            0x233BD70,
            0x233C1FC,
            0x233C65C,
            0x233C7BC,
            0x233C954,
            0x233CB10,
            0x233CEF0,
            0x233D350,
            0x233DB64,
            0x233DCE4,
            0x233DEF4,
            0x233E254,
            0x233EC3C,
            0x2340B74,
            0x2340E00,
            0x23412B4,
            0x2342040,
            0x2342348,
            0x2342D5C,
            0x23430F4,
            0x23433C4,
            0x2343758,
            0x2343848,
            0x234397C,
            0x2343B0C,
        ],
        0x4,
        "Pointer to the global FLOOR_GENERATION_STATUS\n\ntype: struct"
        " floor_generation_status*",
    )

    OFFSET_OF_DUNGEON_N_NORMAL_ITEM_SPAWNS = Symbol(
        [0x5EED8, 0x654C8],
        [0x233BA58, 0x2342048],
        0x4,
        "Offset of the (number of base items + 1) field on the dungeon struct"
        " (0x12AFA)",
    )

    DUNGEON_GRID_COLUMN_BYTES = Symbol(
        [
            0x5F678,
            0x5FAD8,
            0x5FDD0,
            0x5FF8C,
            0x6036C,
            0x607D4,
            0x60A48,
            0x60FDC,
            0x61160,
            0x61378,
            0x616D0,
            0x620B8,
            0x6249C,
            0x62D94,
            0x63178,
            0x63960,
            0x63FF8,
            0x64284,
            0x644B8,
            0x66530,
        ],
        [
            0x233C1F8,
            0x233C658,
            0x233C950,
            0x233CB0C,
            0x233CEEC,
            0x233D354,
            0x233D5C8,
            0x233DB5C,
            0x233DCE0,
            0x233DEF8,
            0x233E250,
            0x233EC38,
            0x233F01C,
            0x233F914,
            0x233FCF8,
            0x23404E0,
            0x2340B78,
            0x2340E04,
            0x2341038,
            0x23430B0,
        ],
        0x4,
        "The number of bytes in one column of the dungeon grid cell array, 450, which"
        " corresponds to a column of 15 grid cells.",
    )

    DEFAULT_MAX_POSITION = Symbol(
        [0x63FFC],
        [0x2340B7C],
        0x4,
        "A large number (9999) to use as a default position for keeping track of"
        " min/max position values",
    )

    OFFSET_OF_DUNGEON_GUARANTEED_ITEM_ID = Symbol(
        [0x654C4, 0x68EE4],
        [0x2342044, 0x2345A64],
        0x4,
        "Offset of the guaranteed item ID field in the dungeon struct (0x2C9E8)",
    )

    FIXED_ROOM_TILE_SPAWN_TABLE = Symbol(
        [0x73E5C],
        [0x23509DC],
        0x2C,
        "Table of tiles that can spawn in fixed rooms, pointed into by the"
        " FIXED_ROOM_TILE_SPAWN_TABLE.\n\nThis is an array of 11 4-byte entries"
        " containing info about one tile each. Info includes the trap ID if a trap,"
        " room ID, and flags.\n\ntype: struct fixed_room_tile_spawn_entry[11]",
    )

    FIXED_ROOM_REVISIT_OVERRIDES = Symbol(
        [0x73EA0],
        [0x2350A20],
        0x100,
        "Table of fixed room IDs, which if nonzero, overrides the normal fixed room ID"
        " for a floor (which is used to index the table) if the dungeon has already"
        " been cleared previously.\n\nOverrides are used to substitute different fixed"
        " room data for things like revisits to story dungeons.\n\ntype: struct"
        " fixed_room_id_8[256]",
    )

    FIXED_ROOM_MONSTER_SPAWN_TABLE = Symbol(
        [0x73FA0],
        [0x2350B20],
        0x1E0,
        "Table of monsters that can spawn in fixed rooms, pointed into by the"
        " FIXED_ROOM_ENTITY_SPAWN_TABLE.\n\nThis is an array of 120 4-byte entries"
        " containing info about one monster each. Info includes the monster ID, stats,"
        " and behavior type.\n\ntype: struct fixed_room_monster_spawn_entry[120]",
    )

    FIXED_ROOM_ITEM_SPAWN_TABLE = Symbol(
        [0x74180],
        [0x2350D00],
        0x1F8,
        "Table of items that can spawn in fixed rooms, pointed into by the"
        " FIXED_ROOM_ENTITY_SPAWN_TABLE.\n\nThis is an array of 63 8-byte entries"
        " containing one item ID each.\n\ntype: struct fixed_room_item_spawn_entry[63]",
    )

    FIXED_ROOM_ENTITY_SPAWN_TABLE = Symbol(
        [0x74378],
        [0x2350EF8],
        0xC9C,
        "Table of entities (items, monsters, tiles) that can spawn in fixed rooms,"
        " which is indexed into by the main data structure for each fixed room.\n\nThis"
        " is an array of 269 entries. Each entry contains 3 pointers (one into"
        " FIXED_ROOM_ITEM_SPAWN_TABLE, one into FIXED_ROOM_MONSTER_SPAWN_TABLE, and one"
        " into FIXED_ROOM_TILE_SPAWN_TABLE), and represents the entities that can spawn"
        " on one specific tile in a fixed room.\n\ntype: struct"
        " fixed_room_entity_spawn_entry[269]",
    )

    STATUS_ICON_ARRAY_MUZZLED = Symbol(
        [0x75248],
        [0x2351DC8],
        0x10,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::muzzled * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_MAGNET_RISE = Symbol(
        [0x75258],
        [0x2351DD8],
        0x10,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::magnet_rise * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_MIRACLE_EYE = Symbol(
        [0x75278],
        [0x2351DF8],
        0x18,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::miracle_eye * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_LEECH_SEED = Symbol(
        [0x75288],
        [0x2351E08],
        0x18,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::leech_seed * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_LONG_TOSS = Symbol(
        [0x752A0],
        [0x2351E20],
        0x18,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::long_toss * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_BLINDED = Symbol(
        [0x752F8],
        [0x2351E78],
        0x28,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::blinded * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_BURN = Symbol(
        [0x75320],
        [0x2351EA0],
        0x28,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::burn * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_SURE_SHOT = Symbol(
        [0x75348],
        [0x2351EC8],
        0x28,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::sure_shot * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_INVISIBLE = Symbol(
        [0x75370],
        [0x2351EF0],
        0x28,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::invisible * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_SLEEP = Symbol(
        [0x75398],
        [0x2351F18],
        0x40,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::sleep * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_CURSE = Symbol(
        [0x753C8],
        [0x2351F48],
        0x38,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::curse * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_FREEZE = Symbol(
        [0x75400],
        [0x2351F80],
        0x40,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::freeze * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_CRINGE = Symbol(
        [0x75440],
        [0x2351FC0],
        0x40,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::cringe * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_BIDE = Symbol(
        [0x75480],
        [0x2352000],
        0x70,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::bide * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_REFLECT = Symbol(
        [0x75580],
        [0x2352100],
        0x90,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::reflect * 8. See UpdateStatusIconFlags for details.",
    )

    DIRECTIONS_XY = Symbol(
        [0x757A8],
        [0x2352328],
        0x20,
        "An array mapping each direction index to its x and y"
        " displacements.\n\nDirections start with 0=down and proceed counterclockwise"
        " (see enum direction_id). Displacements for x and y are interleaved and"
        " encoded as 2-byte signed integers. For example, the first two integers are"
        " [0, 1], which correspond to the x and y displacements for the 'down'"
        " direction (positive y means down).",
    )

    FRACTIONAL_TURN_SEQUENCE = Symbol(
        [0x76342],
        [0x2352EC2],
        0xFA,
        "Read by certain functions that are called by RunFractionalTurn to see if they"
        " should be executed.\n\nArray is accessed via a pointer added to some multiple"
        " of fractional_turn, so that if the resulting memory location is zero, the"
        " function returns.",
    )

    BELLY_DRAIN_IN_WALLS_INT = Symbol(
        [0x767F4],
        [0x2353374],
        0x2,
        "The additional amount by which belly is decreased every turn when inside walls"
        " (integer part)",
    )

    BELLY_DRAIN_IN_WALLS_THOUSANDTHS = Symbol(
        [0x767F6],
        [0x2353376],
        0x2,
        "The additional amount by which belly is decreased every turn when inside walls"
        " (fractional thousandths)",
    )

    SPATK_STAT_IDX = Symbol(
        [0x76B74],
        [0x23536F4],
        0x4,
        "The index (1) of the special attack entry in internal stat structs, such as"
        " the stat modifier array for a monster.",
    )

    ATK_STAT_IDX = Symbol(
        [0x76B78],
        [0x23536F8],
        0x4,
        "The index (0) of the attack entry in internal stat structs, such as the stat"
        " modifier array for a monster.",
    )

    CORNER_CARDINAL_NEIGHBOR_IS_OPEN = Symbol(
        [0x770A4],
        [0x2353C24],
        0x20,
        "An array mapping each (corner index, neighbor direction index) to whether or"
        " not that neighbor is expected to be open floor.\n\nCorners start with"
        " 0=top-left and proceed clockwise. Directions are enumerated as with"
        " DIRECTIONS_XY. The array is indexed by i=(corner_index * N_DIRECTIONS +"
        " direction). An element of 1 (0) means that starting from the specified corner"
        " of a room, moving in the specified direction should lead to an open floor"
        " tile (non-open terrain like a wall).\n\nNote that this array is only used for"
        " the cardinal directions. The elements at odd indexes are unused and"
        " unconditionally set to 0.\n\nThis array is used by the dungeon generation"
        " algorithm when generating room imperfections. See GenerateRoomImperfections.",
    )

    DUNGEON_PTR = Symbol(
        [0x775B8],
        [0x2354138],
        0x4,
        "[Runtime] Pointer to the dungeon struct in dungeon mode.\n\nThis is a 'working"
        " copy' of DUNGEON_PTR_MASTER. The main dungeon engine uses this pointer (or"
        " rather pointers to this pointer) when actually running dungeon mode.\n\ntype:"
        " struct dungeon*",
    )

    DUNGEON_PTR_MASTER = Symbol(
        [0x775BC],
        [0x235413C],
        0x4,
        "[Runtime] Pointer to the dungeon struct in dungeon mode.\n\nThis is a 'master"
        " copy' of the dungeon pointer. The game uses this pointer when doing low-level"
        " memory work (allocation, freeing, zeroing). The normal DUNGEON_PTR is used"
        " for most other dungeon mode work.\n\ntype: struct dungeon*",
    )

    LEADER_PTR = Symbol(
        [0x775DC],
        [0x235415C],
        0x4,
        "[Runtime] Pointer to the current leader of the team.\n\ntype: struct entity*",
    )

    DUNGEON_PRNG_STATE = Symbol(
        [0x775F0],
        [0x2354170],
        0x14,
        "[Runtime] The global PRNG state for dungeon mode, not including the current"
        " values in the secondary sequences.\n\nThis struct holds state for the primary"
        " LCG, as well as the current configuration controlling which LCG to use when"
        " generating random numbers. See DungeonRand16Bit for more information on how"
        " the dungeon PRNG works.\n\ntype: struct prng_state",
    )

    DUNGEON_PRNG_STATE_SECONDARY_VALUES = Symbol(
        [0x77604],
        [0x2354184],
        0x14,
        "[Runtime] An array of 5 integers corresponding to the last value generated for"
        " each secondary LCG sequence.\n\nBased on the assembly, this appears to be its"
        " own global array, separate from DUNGEON_PRNG_STATE.",
    )

    EXCL_ITEM_EFFECTS_WEATHER_ATK_SPEED_BOOST = Symbol(
        [0x77630],
        [0x23541B0],
        0x8,
        "Array of IDs for exclusive item effects that increase attack speed with"
        " certain weather conditions.",
    )

    EXCL_ITEM_EFFECTS_WEATHER_MOVE_SPEED_BOOST = Symbol(
        [0x77638],
        [0x23541B8],
        0x8,
        "Array of IDs for exclusive item effects that increase movement speed with"
        " certain weather conditions.",
    )

    EXCL_ITEM_EFFECTS_WEATHER_NO_STATUS = Symbol(
        [0x77640],
        [0x23541C0],
        0x8,
        "Array of IDs for exclusive item effects that grant status immunity with"
        " certain weather conditions.",
    )

    EXCL_ITEM_EFFECTS_EVASION_BOOST = Symbol(
        [0x77790],
        [0x2354310],
        0x8,
        "Array of IDs for exclusive item effects that grant an evasion boost with"
        " certain weather conditions.",
    )

    DEFAULT_TILE = Symbol(
        [0x777BC],
        [0x235433C],
        0x14,
        "The default tile struct.\n\nThis is just a struct full of zeroes, but is used"
        " as a fallback in various places where a 'default' tile is needed, such as"
        " when a grid index is out of range.\n\ntype: struct tile",
    )

    FIXED_ROOM_DATA_PTR = Symbol(
        [0x7782C],
        [0x23543AC],
        0x4,
        "[Runtime] Pointer to decoded fixed room data loaded from the BALANCE/fixed.bin"
        " file.",
    )

    NECTAR_IQ_BOOST = Symbol(
        [0x40264], [0x231CDE4], None, "IQ boost from ingesting Nectar."
    )


class EuOverlay29Section:
    name = "overlay29"
    description = (
        "The dungeon engine.\n\nThis is the 'main' overlay of dungeon mode. It controls"
        " most things that happen in a Mystery Dungeon, such as dungeon layout"
        " generation, dungeon menus, enemy AI, and generally just running each turn"
        " while within a dungeon."
    )
    loadaddress = 0x22DCB80
    length = 0x77900
    functions = EuOverlay29Functions
    data = EuOverlay29Data


class EuOverlay11Functions:
    FuncThatCallsCommandParsing = Symbol([0xF24], [0x22DDAA4], None, "")

    ScriptCommandParsing = Symbol([0x1B24], [0x22DE6A4], None, "")

    SsbLoad2 = Symbol([0x84BC], [0x22E503C], None, "")

    StationLoadHanger = Symbol([0x8994], [0x22E5514], None, "")

    ScriptStationLoadTalk = Symbol([0x91A4], [0x22E5D24], None, "")

    SsbLoad1 = Symbol([0x9B10], [0x22E6690], None, "")

    ScriptSpecialProcessCall = Symbol(
        [0xAED8],
        [0x22E7A58],
        None,
        "Processes calls to the OPCODE_PROCESS_SPECIAL script opcode.\n\nr0: some"
        " struct containing a callback of some sort, only used for special process ID"
        " 18\nr1: special process ID\nr2: first argument, if relevant? Probably"
        " corresponds to the second parameter of OPCODE_PROCESS_SPECIAL\nr3: second"
        " argument, if relevant? Probably corresponds to the third parameter of"
        " OPCODE_PROCESS_SPECIAL\nreturn: return value of the special process if it has"
        " one, otherwise 0",
    )

    GetSpecialRecruitmentSpecies = Symbol(
        [0xBDFC],
        [0x22E897C],
        None,
        "Returns an entry from RECRUITMENT_TABLE_SPECIES.\n\nNote: This indexes without"
        " doing bounds checking.\n\nr0: index into RECRUITMENT_TABLE_SPECIES\nreturn:"
        " enum monster_id",
    )

    PrepareMenuAcceptTeamMember = Symbol(
        [0xBE40],
        [0x22E89C0],
        None,
        "Implements SPECIAL_PROC_PREPARE_MENU_ACCEPT_TEAM_MEMBER (see"
        " ScriptSpecialProcessCall).\n\nr0: index into RECRUITMENT_TABLE_SPECIES",
    )

    InitRandomNpcJobs = Symbol(
        [0xBEE4],
        [0x22E8A64],
        None,
        "Implements SPECIAL_PROC_INIT_RANDOM_NPC_JOBS (see"
        " ScriptSpecialProcessCall).\n\nr0: job type? 0 is a random NPC job, 1 is a"
        " bottle mission\nr1: ?",
    )

    GetRandomNpcJobType = Symbol(
        [0xBF7C],
        [0x22E8AFC],
        None,
        "Implements SPECIAL_PROC_GET_RANDOM_NPC_JOB_TYPE (see"
        " ScriptSpecialProcessCall).\n\nreturn: job type?",
    )

    GetRandomNpcJobSubtype = Symbol(
        [0xBF94],
        [0x22E8B14],
        None,
        "Implements SPECIAL_PROC_GET_RANDOM_NPC_JOB_SUBTYPE (see"
        " ScriptSpecialProcessCall).\n\nreturn: job subtype?",
    )

    GetRandomNpcJobStillAvailable = Symbol(
        [0xBFB0],
        [0x22E8B30],
        None,
        "Implements SPECIAL_PROC_GET_RANDOM_NPC_JOB_STILL_AVAILABLE (see"
        " ScriptSpecialProcessCall).\n\nreturn: bool",
    )

    AcceptRandomNpcJob = Symbol(
        [0xC018],
        [0x22E8B98],
        None,
        "Implements SPECIAL_PROC_ACCEPT_RANDOM_NPC_JOB (see"
        " ScriptSpecialProcessCall).\n\nreturn: bool",
    )

    GroundMainLoop = Symbol(
        [0xC534],
        [0x22E90B4],
        None,
        "Appears to be the main loop for ground mode.\n\nBased on debug print"
        " statements and general code structure, it seems contain a core loop, and"
        " dispatches to various functions in response to different events.\n\nr0: mode,"
        " which is stored globally and used in switch statements for dispatch\nreturn:"
        " return code",
    )

    GetAllocArenaGround = Symbol(
        [0xD11C],
        [0x22E9C9C],
        None,
        "The GetAllocArena function used for ground mode. See SetMemAllocatorParams for"
        " more information.\n\nr0: initial memory arena pointer, or null\nr1: flags"
        " (see MemAlloc)\nreturn: memory arena pointer, or null",
    )

    GetFreeArenaGround = Symbol(
        [0xD180],
        [0x22E9D00],
        None,
        "The GetFreeArena function used for ground mode. See SetMemAllocatorParams for"
        " more information.\n\nr0: initial memory arena pointer, or null\nr1: pointer"
        " to free\nreturn: memory arena pointer, or null",
    )

    GroundMainReturnDungeon = Symbol(
        [0xD1D4],
        [0x22E9D54],
        None,
        "Implements SPECIAL_PROC_RETURN_DUNGEON (see ScriptSpecialProcessCall).\n\nNo"
        " params.",
    )

    GroundMainNextDay = Symbol(
        [0xD1F8],
        [0x22E9D78],
        None,
        "Implements SPECIAL_PROC_NEXT_DAY (see ScriptSpecialProcessCall).\n\nNo"
        " params.",
    )

    JumpToTitleScreen = Symbol(
        [0xD39C],
        [0x22E9F1C],
        None,
        "Implements SPECIAL_PROC_JUMP_TO_TITLE_SCREEN and SPECIAL_PROC_0x1A (see"
        " ScriptSpecialProcessCall).\n\nr0: int, argument value for"
        " SPECIAL_PROC_JUMP_TO_TITLE_SCREEN and -1 for SPECIAL_PROC_0x1A\nreturn: bool"
        " (but note that the special process ignores this and always returns 0)",
    )

    ReturnToTitleScreen = Symbol(
        [0xD454],
        [0x22E9FD4],
        None,
        "Implements SPECIAL_PROC_RETURN_TO_TITLE_SCREEN (see"
        " ScriptSpecialProcessCall).\n\nr0: fade duration\nreturn: bool (but note that"
        " the special process ignores this and always returns 0)",
    )

    ScriptSpecialProcess0x16 = Symbol(
        [0xD4B4],
        [0x22EA034],
        None,
        "Implements SPECIAL_PROC_0x16 (see ScriptSpecialProcessCall).\n\nr0: bool",
    )

    SprintfStatic = Symbol(
        [0x2CCE8],
        [0x2309868],
        None,
        "Statically defined copy of sprintf(3) in overlay 11. See arm9.yml for more"
        " information.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )

    StatusUpdate = Symbol(
        [0x378F8],
        [0x2314478],
        None,
        "Implements SPECIAL_PROC_STATUS_UPDATE (see ScriptSpecialProcessCall).\n\nNo"
        " params.",
    )


class EuOverlay11Data:
    SCRIPT_OP_CODES = Symbol(
        [0x3C470],
        [0x2318FF0],
        0xBF8,
        "Table of opcodes for the script engine. There are 383 8-byte entries.\n\nThese"
        " opcodes underpin the various ExplorerScript functions you can call in the"
        " SkyTemple SSB debugger.\n\ntype: struct script_opcode_table",
    )

    C_ROUTINES = Symbol(
        [0x40688],
        [0x231D208],
        None,
        "Common routines used within the unionall.ssb script (the master script). There"
        " are 701 8-byte entries.\n\nThese routines underpin the ExplorerScript"
        " coroutines you can call in the SkyTemple SSB debugger.\n\ntype: struct"
        " common_routine_table",
    )

    OBJECTS = Symbol(
        [0x42D5C],
        [0x231F8DC],
        0x1AAC,
        "Table of objects for the script engine, which can be placed in scenes. There"
        " are a version-dependent number of 12-byte entries.\n\ntype: struct"
        " script_object[length / 12]",
    )

    RECRUITMENT_TABLE_LOCATIONS = Symbol(
        [0x44844],
        [0x23213C4],
        0x16,
        "Table of dungeon IDs corresponding to entries in"
        " RECRUITMENT_TABLE_SPECIES.\n\ntype: struct dungeon_id_16[22]",
    )

    RECRUITMENT_TABLE_LEVELS = Symbol(
        [0x4485C],
        [0x23213DC],
        0x2C,
        "Table of levels for recruited Pokémon, corresponding to entries in"
        " RECRUITMENT_TABLE_SPECIES.\n\ntype: uint16_t[22]",
    )

    RECRUITMENT_TABLE_SPECIES = Symbol(
        [0x44888],
        [0x2321408],
        0x2C,
        "Table of Pokémon recruited at special locations, such as at the ends of"
        " certain dungeons (e.g., Dialga or the Seven Treasures legendaries) or during"
        " a cutscene (e.g., Cresselia and Manaphy).\n\nInterestingly, this includes"
        " both Heatran genders. It also includes Darkrai for some reason?\n\ntype:"
        " struct monster_id_16[22]",
    )

    LEVEL_TILEMAP_LIST = Symbol([0x44CDC], [0x232185C], 0x288, "")

    OVERLAY11_OVERLAY_LOAD_TABLE = Symbol(
        [0x4701C],
        [0x2323B9C],
        None,
        "The overlays that can be loaded while this one is loaded.\n\nEach entry is 16"
        " bytes, consisting of:\n- overlay group ID (see arm9.yml or enum"
        " overlay_group_id in the C headers for a mapping between group ID and overlay"
        " number)\n- function pointer to entry point\n- function pointer to"
        " destructor\n- possibly function pointer to frame-update function?",
    )

    UNIONALL_RAM_ADDRESS = Symbol([0x48C64], [0x23257E4], None, "[Runtime]")

    GROUND_STATE_MAP = Symbol([0x48C80], [0x2325800], None, "[Runtime]")

    GROUND_STATE_PTRS = Symbol(
        [0x48CB4],
        [0x2325834],
        0x18,
        "Host pointers to multiple structure used for performing an overworld"
        " scene\n\ntype: struct main_ground_data",
    )


class EuOverlay11Section:
    name = "overlay11"
    description = (
        "The script engine.\n\nThis is the 'main' overlay of ground mode. The script"
        " engine is what runs the ground mode scripts contained in the SCRIPT folder,"
        " which are written in a custom scripting language. These scripts encode things"
        " like cutscenes, screen transitions, ground mode events, and tons of other"
        " things related to ground mode."
    )
    loadaddress = 0x22DCB80
    length = 0x48E40
    functions = EuOverlay11Functions
    data = EuOverlay11Data


class EuOverlay25Functions:
    pass


class EuOverlay25Data:
    APPRAISAL_MENU_CONFIRM = Symbol([0x1374], [0x238BFF4], 0x18, "")

    APPRAISAL_MAIN_MENU = Symbol([0x138C], [0x238C00C], 0x20, "")

    APPRAISAL_SUBMENU = Symbol([0x13AC], [0x238C02C], 0x20, "")


class EuOverlay25Section:
    name = "overlay25"
    description = "Controls Xatu Appraisal."
    loadaddress = 0x238AC80
    length = 0x14C0
    functions = EuOverlay25Functions
    data = EuOverlay25Data


class EuArm9Functions:
    InitMemAllocTable = Symbol(
        [0xDE0],
        [0x2000DE0],
        None,
        "Initializes MEMORY_ALLOCATION_TABLE.\n\nSets up the default memory arena, sets"
        " the default memory allocator parameters (calls SetMemAllocatorParams(0, 0)),"
        " and does some other stuff.\n\nNo params.",
    )

    SetMemAllocatorParams = Symbol(
        [0xE70],
        [0x2000E70],
        None,
        "Sets global parameters for the memory allocator.\n\nThis includes"
        " MEMORY_ALLOCATION_ARENA_GETTERS and some other stuff.\n\nDungeon mode uses"
        " the default arena getters. Ground mode uses its own arena getters, which are"
        " defined in overlay 11 and set (by calling this function) at the start of"
        " GroundMainLoop.\n\nr0: GetAllocArena function pointer (GetAllocArenaDefault"
        " is used if null)\nr1: GetFreeArena function pointer (GetFreeArenaDefault is"
        " used if null)",
    )

    GetAllocArenaDefault = Symbol(
        [0xEC0],
        [0x2000EC0],
        None,
        "The default function for retrieving the arena for memory allocations. This"
        " function always just returns the initial arena pointer.\n\nr0: initial memory"
        " arena pointer, or null\nr1: flags (see MemAlloc)\nreturn: memory arena"
        " pointer, or null",
    )

    GetFreeArenaDefault = Symbol(
        [0xEC4],
        [0x2000EC4],
        None,
        "The default function for retrieving the arena for memory freeing. This"
        " function always just returns the initial arena pointer.\n\nr0: initial memory"
        " arena pointer, or null\nr1: pointer to free\nreturn: memory arena pointer, or"
        " null",
    )

    InitMemArena = Symbol(
        [0xEC8],
        [0x2000EC8],
        None,
        "Initializes a new memory arena with the given specifications, and records it"
        " in the global MEMORY_ALLOCATION_TABLE.\n\nr0: arena struct to be"
        " initialized\nr1: memory region to be owned by the arena, as {pointer,"
        " length}\nr2: pointer to block metadata array for the arena to use\nr3:"
        " maximum number of blocks that the arena can hold",
    )

    MemAllocFlagsToBlockType = Symbol(
        [0xF44],
        [0x2000F44],
        None,
        "Converts the internal alloc flags bitfield (struct mem_block field 0x4) to the"
        " block type bitfield (struct mem_block field 0x0).\n\nr0: internal alloc"
        " flags\nreturn: block type flags",
    )

    FindAvailableMemBlock = Symbol(
        [0xF88],
        [0x2000F88],
        None,
        "Searches through the given memory arena for a block with enough free"
        " space.\n\nBlocks are searched in reverse order. For object allocations (i.e.,"
        " not arenas), the block with the smallest amount of free space that still"
        " suffices is returned. For arena allocations, the first satisfactory block"
        " found is returned.\n\nr0: memory arena to search\nr1: internal alloc"
        " flags\nr2: amount of space needed, in bytes\nreturn: index of the located"
        " block in the arena's block array, or -1 if nothing is available",
    )

    SplitMemBlock = Symbol(
        [0x1070],
        [0x2001070],
        None,
        "Given a memory block at a given index, splits off another memory block of the"
        " specified size from the end.\n\nSince blocks are stored in an array on the"
        " memory arena struct, this is essentially an insertion operation, plus some"
        " processing on the block being split and its child.\n\nr0: memory arena\nr1:"
        " block index\nr2: internal alloc flags\nr3: number of bytes to split"
        " off\nstack[0]: user alloc flags (to assign to the new block)\nreturn: the"
        " newly split-off memory block",
    )

    MemAlloc = Symbol(
        [0x1170],
        [0x2001170],
        None,
        "Allocates some memory on the heap, returning a pointer to the starting"
        " address.\n\nMemory allocation is done with region-based memory management."
        " See MEMORY_ALLOCATION_TABLE for more information.\n\nThis function is just a"
        " wrapper around MemLocateSet.\n\nr0: length in bytes\nr1: flags (see the"
        " comment on struct mem_block::user_flags)\nreturn: pointer",
    )

    MemFree = Symbol(
        [0x1188],
        [0x2001188],
        None,
        "Frees heap-allocated memory.\n\nThis function is just a wrapper around"
        " MemLocateUnset.\n\nr0: pointer",
    )

    MemArenaAlloc = Symbol(
        [0x119C],
        [0x200119C],
        None,
        "Allocates some memory on the heap and creates a new global memory arena with"
        " it.\n\nThe actual allocation part works similarly to the normal"
        " MemAlloc.\n\nr0: desired parent memory arena, or null\nr1: length of the"
        " arena in bytes\nr2: maximum number of blocks that the arena can hold\nr3:"
        " flags (see MemAlloc)\nreturn: memory arena pointer",
    )

    CreateMemArena = Symbol(
        [0x1280],
        [0x2001280],
        None,
        "Creates a new memory arena within a given block of memory.\n\nThis is"
        " essentially a wrapper around InitMemArena, accounting for the space needed by"
        " the arena metadata.\n\nr0: memory region in which to create the arena, as"
        " {pointer, length}\nr1: maximum number of blocks that the arena can"
        " hold\nreturn: memory arena pointer",
    )

    MemLocateSet = Symbol(
        [0x1390],
        [0x2001390],
        None,
        "The implementation for MemAlloc.\n\nAt a high level, memory is allocated by"
        " choosing a memory arena, looking through blocks in the memory arena until a"
        " free one that's large enough is found, then splitting off a new memory block"
        " of the needed size.\n\nThis function is not fallible, i.e., it hangs the"
        " whole program on failure, so callers can assume it never fails.\n\nThe name"
        " for this function comes from the error message logged on failure, and it"
        " reflects what the function does: locate an available block of memory and set"
        " it up for the caller.\n\nr0: desired memory arena for allocation, or null"
        " (MemAlloc passes null)\nr1: length in bytes\nr2: flags (see"
        " MemAlloc)\nreturn: pointer to allocated memory",
    )

    MemLocateUnset = Symbol(
        [0x1638],
        [0x2001638],
        None,
        "The implementation for MemFree.\n\nAt a high level, memory is freed by"
        " locating the pointer in its memory arena (searching block-by-block) and"
        " emptying the block so it's available for future allocations, and merging it"
        " with neighboring blocks if they're available.\n\nr0: desired memory arena for"
        " freeing, or null (MemFree passes null)\nr1: pointer to free",
    )

    RoundUpDiv256 = Symbol(
        [0x1894],
        [0x2001894],
        None,
        "Divide a number by 256 and round up to the nearest integer.\n\nr0:"
        " number\nreturn: number // 256",
    )

    MultiplyByFixedPoint = Symbol(
        [0x1A54],
        [0x2001A54],
        None,
        "Multiply a signed integer x by a signed binary fixed-point multiplier (8"
        " fraction bits).\n\nr0: x\nr1: multiplier\nreturn: x * multiplier",
    )

    UMultiplyByFixedPoint = Symbol(
        [0x1B0C],
        [0x2001B0C],
        None,
        "Multiplies an unsigned integer x by an unsigned binary fixed-point multiplier"
        " (8 fraction bits).\n\nr0: x\nr1: multiplier\nreturn: x * multiplier",
    )

    GetRngSeed = Symbol(
        [0x222C], [0x200222C], None, "Get the current value of PRNG_SEQUENCE_NUM."
    )

    SetRngSeed = Symbol(
        [0x223C],
        [0x200223C],
        None,
        "Seed PRNG_SEQUENCE_NUM to a given value.\n\nr0: seed",
    )

    Rand16Bit = Symbol(
        [0x224C],
        [0x200224C],
        None,
        "Computes a pseudorandom 16-bit integer using the general-purpose PRNG.\n\nNote"
        " that much of dungeon mode uses its own (slightly higher-quality) PRNG within"
        " overlay 29. See overlay29.yml for more information.\n\nRandom numbers are"
        " generated with a linear congruential generator (LCG), using a modulus of"
        " 2^16, a multiplier of 109, and an increment of 1021. I.e., the recurrence"
        " relation is `x = (109*x_prev + 1021) % 2^16`.\n\nThe LCG has a hard-coded"
        " seed of 13452 (0x348C), but can be seeded with a call to"
        " SetRngSeed.\n\nreturn: pseudorandom int on the interval [0, 65535]",
    )

    RandInt = Symbol(
        [0x2274],
        [0x2002274],
        None,
        "Compute a pseudorandom integer under a given maximum value using the"
        " general-purpose PRNG.\n\nThis function relies on a single call to Rand16Bit."
        " Even though it takes a 32-bit integer as input, the number of unique outcomes"
        " is capped at 2^16.\n\nr0: high\nreturn: pseudorandom integer on the interval"
        " [0, high - 1]",
    )

    RandRange = Symbol(
        [0x228C],
        [0x200228C],
        None,
        "Compute a pseudorandom value between two integers using the general-purpose"
        " PRNG.\n\nThis function relies on a single call to Rand16Bit. Even though it"
        " takes 32-bit integers as input, the number of unique outcomes is capped at"
        " 2^16.\n\nr0: x\nr1: y\nreturn: pseudorandom integer on the interval [x, y"
        " - 1]",
    )

    Rand32Bit = Symbol(
        [0x22AC],
        [0x20022AC],
        None,
        "Computes a random 32-bit integer using the general-purpose PRNG. The upper and"
        " lower 16 bits are each generated with a separate call to Rand16Bit (so this"
        " function advances the PRNG twice).\n\nreturn: pseudorandom int on the"
        " interval [0, 4294967295]",
    )

    RandIntSafe = Symbol(
        [0x22F8],
        [0x20022F8],
        None,
        "Same as RandInt, except explicitly masking out the upper 16 bits of the output"
        " from Rand16Bit (which should be zero anyway).\n\nr0: high\nreturn:"
        " pseudorandom integer on the interval [0, high - 1]",
    )

    RandRangeSafe = Symbol(
        [0x2318],
        [0x2002318],
        None,
        "Like RandRange, except reordering the inputs as needed, and explicitly masking"
        " out the upper 16 bits of the output from Rand16Bit (which should be zero"
        " anyway).\n\nr0: x\nr1: y\nreturn: pseudorandom integer on the interval"
        " [min(x, y), max(x, y) - 1]",
    )

    WaitForever = Symbol(
        [0x2438],
        [0x2002438],
        None,
        "Sets some program state and calls WaitForInterrupt in an infinite"
        " loop.\n\nThis is called on fatal errors to hang the program"
        " indefinitely.\n\nNo params.",
    )

    InitMemAllocTableVeneer = Symbol(
        [0x321C],
        [0x200321C],
        None,
        "Likely a linker-generated veneer for InitMemAllocTable.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nNo"
        " params.",
    )

    MemZero = Symbol(
        [0x3250], [0x2003250], None, "Zeroes a buffer.\n\nr0: ptr\nr1: len"
    )

    MemcpySimple = Symbol(
        [0x32E4],
        [0x20032E4],
        None,
        "A simple implementation of the memcpy(3) C library function.\n\nThis function"
        " was probably manually implemented by the developers. See Memcpy for what's"
        " probably the real libc function.\n\nThis function copies from src to dst in"
        " backwards byte order, so this is safe to call for overlapping src and dst if"
        " src <= dst.\n\nr0: dest\nr1: src\nr2: n",
    )

    TaskProcBoot = Symbol(
        [0x3328],
        [0x2003328],
        None,
        "Probably related to booting the game?\n\nThis function prints the debug"
        " message 'task proc boot'.\n\nNo params.",
    )

    EnableAllInterrupts = Symbol(
        [0x3608],
        [0x2003608],
        None,
        "Sets the Interrupt Master Enable (IME) register to 1, which enables all CPU"
        " interrupts (if enabled in the Interrupt Enable (IE) register).\n\nSee"
        " https://problemkaputt.de/gbatek.htm#dsiomaps.\n\nreturn: old value in the IME"
        " register",
    )

    GetTime = Symbol(
        [0x37B4],
        [0x20037B4],
        None,
        "Seems to get the current (system?) time as an IEEE 754 floating-point"
        " number.\n\nreturn: current time (maybe in seconds?)",
    )

    DisableAllInterrupts = Symbol(
        [0x3824],
        [0x2003824],
        None,
        "Sets the Interrupt Master Enable (IME) register to 0, which disables all CPU"
        " interrupts (even if enabled in the Interrupt Enable (IE) register).\n\nSee"
        " https://problemkaputt.de/gbatek.htm#dsiomaps.\n\nreturn: old value in the IME"
        " register",
    )

    SoundResume = Symbol(
        [0x3CC4],
        [0x2003CC4],
        None,
        "Probably resumes the sound player if paused?\n\nThis function prints the debug"
        " string 'sound resume'.",
    )

    CardPullOutWithStatus = Symbol(
        [0x3D2C],
        [0x2003D2C],
        None,
        "Probably aborts the program with some status code? It seems to serve a similar"
        " purpose to the exit(3) function.\n\nThis function prints the debug string"
        " 'card pull out %d' with the status code.\n\nr0: status code",
    )

    CardPullOut = Symbol(
        [0x3D70],
        [0x2003D70],
        None,
        "Sets some global flag that probably triggers system exit?\n\nThis function"
        " prints the debug string 'card pull out'.\n\nNo params.",
    )

    CardBackupError = Symbol(
        [0x3D94],
        [0x2003D94],
        None,
        "Sets some global flag that maybe indicates a save error?\n\nThis function"
        " prints the debug string 'card backup error'.\n\nNo params.",
    )

    HaltProcessDisp = Symbol(
        [0x3DB8],
        [0x2003DB8],
        None,
        "Maybe halts the process display?\n\nThis function prints the debug string"
        " 'halt process disp %d' with the status code.\n\nr0: status code",
    )

    OverlayIsLoaded = Symbol(
        [0x3ED0],
        [0x2003ED0],
        None,
        "Checks if an overlay with a certain group ID is currently loaded.\n\nSee the"
        " LOADED_OVERLAY_GROUP_* data symbols or enum overlay_group_id in the C headers"
        " for a mapping between group ID and overlay number.\n\nr0: group ID of the"
        " overlay to check. A group ID of 0 denotes no overlay, and the return value"
        " will always be true in this case.\nreturn: bool",
    )

    LoadOverlay = Symbol(
        [0x40AC],
        [0x20040AC],
        None,
        "Loads an overlay from ROM by its group ID.\n\nSee the LOADED_OVERLAY_GROUP_*"
        " data symbols or enum overlay_group_id in the C headers for a mapping between"
        " group ID and overlay number.\n\nr0: group ID of the overlay to load",
    )

    UnloadOverlay = Symbol(
        [0x4868],
        [0x2004868],
        None,
        "Unloads an overlay from ROM by its group ID.\n\nSee the LOADED_OVERLAY_GROUP_*"
        " data symbols or enum overlay_group_id in the C headers for a mapping between"
        " group ID and overlay number.\n\nr0: group ID of the overlay to"
        " unload\nothers: ?",
    )

    EuclideanNorm = Symbol(
        [0x5050, 0x50B0],
        [0x2005050, 0x20050B0],
        None,
        "Computes the Euclidean norm of a two-component integer array, sort of like"
        " hypotf(3).\n\nr0: integer array [x, y]\nreturn: sqrt(x*x + y*y)",
    )

    ClampComponentAbs = Symbol(
        [0x5110],
        [0x2005110],
        None,
        "Clamps the absolute values in a two-component integer array.\n\nGiven an"
        " integer array [x, y] and a maximum absolute value M, clamps each element of"
        " the array to M such that the output array is [min(max(x, -M), M), min(max(y,"
        " -M), M)].\n\nr0: 2-element integer array, will be mutated\nr1: max absolute"
        " value",
    )

    KeyWaitInit = Symbol(
        [0x6DA4],
        [0x2006DA4],
        None,
        "Implements (most of?) SPECIAL_PROC_KEY_WAIT_INIT (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    DataTransferInit = Symbol(
        [0x8168],
        [0x2008168],
        None,
        "Initializes data transfer mode to get data from the ROM cartridge.\n\nNo"
        " params.",
    )

    DataTransferStop = Symbol(
        [0x8194],
        [0x2008194],
        None,
        "Finalizes data transfer from the ROM cartridge.\n\nThis function must always"
        " be called if DataTransferInit was called, or the game will crash.\n\nNo"
        " params.",
    )

    FileInitVeneer = Symbol(
        [0x8204],
        [0x2008204],
        None,
        "Likely a linker-generated veneer for FileInit.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nr0:"
        " file_stream pointer",
    )

    FileOpen = Symbol(
        [0x8210],
        [0x2008210],
        None,
        "Opens a file from the ROM file system at the given path, sort of like C's"
        " fopen(3) library function.\n\nr0: file_stream pointer\nr1: file path string",
    )

    FileGetSize = Symbol(
        [0x8244],
        [0x2008244],
        None,
        "Gets the size of an open file.\n\nr0: file_stream pointer\nreturn: file size",
    )

    FileRead = Symbol(
        [0x8254],
        [0x2008254],
        None,
        "Reads the contents of a file into the given buffer, and moves the file cursor"
        " accordingly.\n\nData transfer mode must have been initialized (with"
        " DataTransferInit) prior to calling this function. This function looks like"
        " it's doing something akin to calling read(2) or fread(3) in a loop until all"
        " the bytes have been successfully read.\n\nr0: file_stream pointer\nr1:"
        " [output] buffer\nr2: number of bytes to read\nreturn: number of bytes read",
    )

    FileSeek = Symbol(
        [0x82A8],
        [0x20082A8],
        None,
        "Sets a file stream's position indicator.\n\nThis function has the a similar"
        " API to the fseek(3) library function from C, including using the same codes"
        " for the `whence` parameter:\n- SEEK_SET=0\n- SEEK_CUR=1\n- SEEK_END=2\n\nr0:"
        " file_stream pointer\nr1: offset\nr2: whence",
    )

    FileClose = Symbol(
        [0x82C4],
        [0x20082C4],
        None,
        "Closes a file.\n\nData transfer mode must have been initialized (with"
        " DataTransferInit) prior to calling this function.\n\nNote: It is possible to"
        " keep a file stream open even if data transfer mode has been stopped, in which"
        " case the file stream can be used again if data transfer mode is"
        " reinitialized.\n\nr0: file_stream pointer",
    )

    LoadFileFromRom = Symbol(
        [0x8C3C],
        [0x2008C3C],
        None,
        "Loads a file from ROM by filepath into a heap-allocated buffer.\n\nr0:"
        " [output] pointer to an IO struct {ptr, len}\nr1: file path string"
        " pointer\nr2: flags",
    )

    GetDebugFlag1 = Symbol(
        [0xC198], [0x200C198], None, "Just returns 0 in the final binary."
    )

    SetDebugFlag1 = Symbol([0xC1A0], [0x200C1A0], None, "A no-op in the final binary.")

    AppendProgPos = Symbol(
        [0xC1A8],
        [0x200C1A8],
        None,
        "Write a base message into a string and append the file name and line number to"
        " the end in the format 'file = '%s'  line = %5d\n'.\n\nIf no program position"
        " info is given, 'ProgPos info NULL\n' is appended instead.\n\nr0: [output]"
        " str\nr1: program position info\nr2: base message\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )

    DebugPrintTrace = Symbol(
        [0xC1F4],
        [0x200C1F4],
        None,
        "Would log a printf format string tagged with the file name and line number in"
        " the debug binary.\n\nThis still constructs the string, but doesn't actually"
        " do anything with it in the final binary.\n\nIf message is a null pointer, the"
        " string '  Print  ' is used instead.\n\nr0: message\nr1: program position info"
        " (can be null)",
    )

    DebugPrint0 = Symbol(
        [0xC250, 0xC284],
        [0x200C250, 0x200C284],
        None,
        "Would log a printf format string in the debug binary.\n\nThis still constructs"
        " the string with Vsprintf, but doesn't actually do anything with it in the"
        " final binary.\n\nr0: format\n...: variadic",
    )

    GetDebugFlag2 = Symbol(
        [0xC2BC], [0x200C2BC], None, "Just returns 0 in the final binary."
    )

    SetDebugFlag2 = Symbol([0xC2C4], [0x200C2C4], None, "A no-op in the final binary.")

    DebugPrint = Symbol(
        [0xC2C8],
        [0x200C2C8],
        None,
        "Would log a printf format string in the debug binary. A no-op in the final"
        " binary.\n\nr0: log level\nr1: format\n...: variadic",
    )

    FatalError = Symbol(
        [0xC2E4],
        [0x200C2E4],
        None,
        "Logs some debug messages, then hangs the process.\n\nThis function is called"
        " in lots of places to bail on a fatal error. Looking at the static data"
        " callers use to fill in the program position info is informative, as it tells"
        " you the original file name (probably from the standard __FILE__ macro) and"
        " line number (probably from the standard __LINE__ macro) in the source"
        " code.\n\nr0: program position info\nr1: format\n...: variadic",
    )

    OpenAllPackFiles = Symbol(
        [0xC364],
        [0x200C364],
        None,
        "Open the 6 files at PACK_FILE_PATHS_TABLE into PACK_FILE_OPENED. Called during"
        " game initialisation.\n\nNo params.",
    )

    GetFileLengthInPackWithPackNb = Symbol(
        [0xC3C4],
        [0x200C3C4],
        None,
        "Call GetFileLengthInPack after looking up the global Pack archive by its"
        " number\n\nr0: pack file number\nr1: file number\nreturn: size of the file in"
        " bytes from the Pack Table of Content",
    )

    LoadFileInPackWithPackId = Symbol(
        [0xC3E4],
        [0x200C3E4],
        None,
        "Call LoadFileInPack after looking up the global Pack archive by its"
        " identifier\n\nr0: pack file identifier\nr1: [output] target buffer\nr2: file"
        " index\nreturn: number of read bytes (identical to the length of the pack from"
        " the Table of Content)",
    )

    AllocAndLoadFileInPack = Symbol(
        [0xC410],
        [0x200C410],
        None,
        "Allocate a file and load a file from the pack archive inside.\nThe data"
        " pointed by the pointer in the output need to be freed once is not needed"
        " anymore.\n\nr0: pack file identifier\nr1: file index\nr2: [output] result"
        " struct (will contain length and pointer)\nr3: allocation flags",
    )

    OpenPackFile = Symbol(
        [0xC468],
        [0x200C468],
        None,
        "Open a Pack file, to be read later. Initialise the output structure.\n\nr0:"
        " [output] pack file struct\nr1: file name",
    )

    GetFileLengthInPack = Symbol(
        [0xC4FC],
        [0x200C4FC],
        None,
        "Get the length of a file entry from a Pack archive\n\nr0: pack file"
        " struct\nr1: file index\nreturn: size of the file in bytes from the Pack Table"
        " of Content",
    )

    LoadFileInPack = Symbol(
        [0xC50C],
        [0x200C50C],
        None,
        "Load the indexed file from the Pack archive, itself loaded from the"
        " ROM.\n\nr0: pack file struct\nr1: [output] target buffer\nr2: file"
        " index\nreturn: number of read bytes (identical to the length of the pack from"
        " the Table of Content)",
    )

    IsAuraBow = Symbol(
        [0xCC9C],
        [0x200CC9C],
        None,
        "Checks if an item is one of the aura bows received at the start of the"
        " game.\n\nr0: item ID\nreturn: bool",
    )

    SprintfStatic = Symbol(
        [
            0xD6BC,
            0xE808,
            0x13800,
            0x177C4,
            0x17ADC,
            0x2378C,
            0x239B0,
            0x3822C,
            0x39734,
            0x3AC6C,
            0x3D2A0,
            0x41A48,
            0x42DA0,
            0x52750,
            0x54DDC,
            0x60D64,
        ],
        [
            0x200D6BC,
            0x200E808,
            0x2013800,
            0x20177C4,
            0x2017ADC,
            0x202378C,
            0x20239B0,
            0x203822C,
            0x2039734,
            0x203AC6C,
            0x203D2A0,
            0x2041A48,
            0x2042DA0,
            0x2052750,
            0x2054DDC,
            0x2060D64,
        ],
        None,
        "Functionally the same as Sprintf, just defined statically in many different"
        " places.\n\nSince this is essentially just a wrapper around vsprintf(3), this"
        " function was probably statically defined in a header somewhere and included"
        " in a bunch of different places. See the actual Sprintf for the one in"
        " libc.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of characters"
        " printed, excluding the null-terminator",
    )

    SetMoneyCarried = Symbol(
        [0xEDC4],
        [0x200EDC4],
        None,
        "Sets the amount of money the player is carrying, clamping the value to the"
        " range [0, MAX_MONEY_CARRIED].\n\nr0: new value",
    )

    IsBagFull = Symbol(
        [0xEE68],
        [0x200EE68],
        None,
        "Implements SPECIAL_PROC_IS_BAG_FULL (see ScriptSpecialProcessCall).\n\nreturn:"
        " bool",
    )

    CountItemTypeInBag = Symbol(
        [0xEF30],
        [0x200EF30],
        None,
        "Implements SPECIAL_PROC_COUNT_ITEM_TYPE_IN_BAG (see"
        " ScriptSpecialProcessCall).\n\nr0: item ID\nreturn: number of items of the"
        " specified ID in the bag",
    )

    AddItemToBag = Symbol(
        [0xF8F4],
        [0x200F8F4],
        None,
        "Implements SPECIAL_PROC_ADD_ITEM_TO_BAG (see ScriptSpecialProcessCall).\n\nr0:"
        " pointer to an owned_item\nreturn: bool",
    )

    ScriptSpecialProcess0x39 = Symbol(
        [0xFDFC],
        [0x200FDFC],
        None,
        "Implements SPECIAL_PROC_0x39 (see ScriptSpecialProcessCall).\n\nreturn: bool",
    )

    CountItemTypeInStorage = Symbol(
        [0xFF8C],
        [0x200FF8C],
        None,
        "Implements SPECIAL_PROC_COUNT_ITEM_TYPE_IN_STORAGE (see"
        " ScriptSpecialProcessCall).\n\nr0: pointer to an owned_item\nreturn: number of"
        " items of the specified ID in storage",
    )

    RemoveItemsTypeInStorage = Symbol(
        [0x1028C],
        [0x201028C],
        None,
        "Probably? Implements SPECIAL_PROC_0x2A (see ScriptSpecialProcessCall).\n\nr0:"
        " pointer to an owned_item\nreturn: bool",
    )

    AddItemToStorage = Symbol(
        [0x103C4],
        [0x20103C4],
        None,
        "Implements SPECIAL_PROC_ADD_ITEM_TO_STORAGE (see"
        " ScriptSpecialProcessCall).\n\nr0: pointer to an owned_item\nreturn: bool",
    )

    SetMoneyStored = Symbol(
        [0x107CC],
        [0x20107CC],
        None,
        "Sets the amount of money the player has stored in the Duskull Bank, clamping"
        " the value to the range [0, MAX_MONEY_STORED].\n\nr0: new value",
    )

    GetExclusiveItemOffset = Symbol(
        [0x10EE8],
        [0x2010EE8],
        None,
        "Gets the exclusive item offset, which is the item ID relative to that of the"
        " first exclusive item, the Prism Ruff.\n\nr0: item ID\nreturn: offset",
    )

    ApplyExclusiveItemStatBoosts = Symbol(
        [0x10F0C],
        [0x2010F0C],
        None,
        "Applies stat boosts from an exclusive item.\n\nr0: item ID\nr1: pointer to"
        " attack stat to modify\nr2: pointer to special attack stat to modify\nr3:"
        " pointer to defense stat to modify\nstack[0]: pointer to special defense stat"
        " to modify",
    )

    SetExclusiveItemEffect = Symbol(
        [0x11028],
        [0x2011028],
        None,
        "Sets the bit for an exclusive item effect.\n\nr0: pointer to the effects"
        " bitvector to modify\nr1: exclusive item effect ID",
    )

    ExclusiveItemEffectFlagTest = Symbol(
        [0x1104C],
        [0x201104C],
        None,
        "Tests the exclusive item bitvector for a specific exclusive item"
        " effect.\n\nr0: the effects bitvector to test\nr1: exclusive item effect"
        " ID\nreturn: bool",
    )

    ApplyGummiBoostsGroundMode = Symbol(
        [0x11944],
        [0x2011944],
        None,
        "Applies the IQ boosts from eating a Gummi to the target monster.\n\nr0:"
        " Pointer to something\nr1: Pointer to something\nr2: Pointer to something\nr3:"
        " Pointer to something\nstack[0]: ?\nstack[1]: ?\nstack[2]: Pointer to a buffer"
        " to store some result into",
    )

    GetMoveTargetAndRange = Symbol(
        [0x138E8],
        [0x20138E8],
        None,
        "Gets the move target-and-range field. See struct move_target_and_range in the"
        " C headers.\n\nr0: move pointer\nr1: AI flag (every move has two"
        " target-and-range fields, one for players and one for AI)\nreturn: move target"
        " and range",
    )

    GetMoveType = Symbol(
        [0x1390C],
        [0x201390C],
        None,
        "Gets the type of a move\n\nr0: Pointer to move data\nreturn: Type of the move",
    )

    GetMoveAiWeight = Symbol(
        [0x13A34],
        [0x2013A34],
        None,
        "Gets the AI weight of a move\n\nr0: Pointer to move data\nreturn: AI weight of"
        " the move",
    )

    GetMoveBasePower = Symbol(
        [0x13A74],
        [0x2013A74],
        None,
        "Gets the base power of a move from the move data table.\n\nr0: move"
        " pointer\nreturn: base power",
    )

    GetMoveAccuracyOrAiChance = Symbol(
        [0x13AB4],
        [0x2013AB4],
        None,
        "Gets one of the two accuracy values of a move or its"
        " ai_condition_random_chance field.\n\nr0: Move pointer\nr1: 0 to get the"
        " move's first accuracy1 field, 1 to get its accuracy2, 2 to get its"
        " ai_condition_random_chance.\nreturn: Move's accuracy1, accuracy2 or"
        " ai_condition_random_chance",
    )

    GetMaxPp = Symbol(
        [0x13AF8],
        [0x2013AF8],
        None,
        "Gets the maximum PP for a given move.\n\nr0: move pointer\nreturn: max PP for"
        " the given move, capped at 99",
    )

    GetMoveCritChance = Symbol(
        [0x13BB8],
        [0x2013BB8],
        None,
        "Gets the critical hit chance of a move.\n\nr0: move pointer\nreturn: base"
        " power",
    )

    IsMoveRangeString19 = Symbol(
        [0x13CAC],
        [0x2013CAC],
        None,
        "Returns whether a move's range string is 19 ('User').\n\nr0: Move"
        " pointer\nreturn: True if the move's range string field has a value of 19.",
    )

    IsRecoilMove = Symbol(
        [0x13EBC],
        [0x2013EBC],
        None,
        "Checks if the given move is a recoil move (affected by Reckless).\n\nr0: move"
        " ID\nreturn: bool",
    )

    IsPunchMove = Symbol(
        [0x14DC0],
        [0x2014DC0],
        None,
        "Checks if the given move is a punch move (affected by Iron Fist).\n\nr0: move"
        " ID\nreturn: bool",
    )

    GetMoveCategory = Symbol(
        [0x15270],
        [0x2015270],
        None,
        "Gets a move's category (physical, special, status).\n\nr0: move ID\nreturn:"
        " move category enum",
    )

    LoadWteFromRom = Symbol(
        [0x1DEE8],
        [0x201DEE8],
        None,
        "Loads a SIR0-wrapped WTE file from ROM, and returns a handle to it\n\nr0:"
        " [output] pointer to wte handle\nr1: file path string\nr2: load file flags",
    )

    LoadWteFromFileDirectory = Symbol(
        [0x1DF60],
        [0x201DF60],
        None,
        "Loads a SIR0-wrapped WTE file from a file directory, and returns a handle to"
        " it\n\nr0: [output] pointer to wte handle\nr1: file directory id\nr2: file"
        " index\nr3: malloc flags",
    )

    UnloadWte = Symbol(
        [0x1DFB4],
        [0x201DFB4],
        None,
        "Frees the buffer used to store the WTE data in the handle, and sets both"
        " pointers to null\n\nr0: pointer to wte handle",
    )

    HandleSir0Translation = Symbol(
        [0x1F550],
        [0x201F550],
        None,
        "Translates the offsets in a SIR0 file into NDS memory addresses, changes the"
        " magic number to SirO (opened), and returns a pointer to the first pointer"
        " specified in the SIR0 header (beginning of the data).\n\nr0: [output] double"
        " pointer to beginning of data\nr1: pointer to source file buffer",
    )

    HandleSir0TranslationVeneer = Symbol(
        [0x1F628],
        [0x201F628],
        None,
        "Likely a linker-generated veneer for HandleSir0Translation.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nr0:"
        " [output] double pointer to beginning of data\nr1: pointer to source file"
        " buffer",
    )

    GetLanguageType = Symbol(
        [0x20688],
        [0x2020688],
        None,
        "Gets the language type.\n\nThis is the value backing the special LANGUAGE_TYPE"
        " script variable.\n\nreturn: language type",
    )

    GetLanguage = Symbol(
        [0x206B0],
        [0x20206B0],
        None,
        "Gets the single-byte language ID of the current program.\n\nThe language ID"
        " appears to be used to index some global tables.\n\nreturn: language ID",
    )

    PreprocessString = Symbol(
        [0x225EC],
        [0x20225EC],
        None,
        "An enhanced sprintf, which recognizes certain tags and replaces them with"
        " appropiate game values.\nThis function can also be used to simply insert"
        " values passed within the preprocessor args\n\nThe tags utilized for this"
        " function are lowercase, it might produce uppercase tags\nthat only are used"
        " when the text is being typewrited into a message box\n\nr0: [output]"
        " formatted string\nr1: maximum capacity of the output buffer\nr2: input format"
        " string\nr3: preprocessor flags\nstack[0]: pointer to preprocessor args",
    )

    StrcpySimple = Symbol(
        [0x253CC],
        [0x20253CC],
        None,
        "A simple implementation of the strcpy(3) C library function.\n\nThis function"
        " was probably manually implemented by the developers. See Strcpy for what's"
        " probably the real libc function.\n\nr0: dest\nr1: src",
    )

    StrncpySimple = Symbol(
        [0x253E8],
        [0x20253E8],
        None,
        "A simple implementation of the strncpy(3) C library function.\n\nThis function"
        " was probably manually implemented by the developers. See Strncpy for what's"
        " probably the real libc function.\n\nr0: dest\nr1: src\nr2: n",
    )

    StringFromMessageId = Symbol(
        [0x25B90],
        [0x2025B90],
        None,
        "Gets the string corresponding to a given message ID.\n\nr0: message"
        " ID\nreturn: string from the string files with the given message ID",
    )

    SetScreenWindowsColor = Symbol(
        [0x27D5C],
        [0x2027D5C],
        None,
        "Sets the palette of the frames of windows in the specified screen\n\nr0:"
        " palette index\nr1: is upper screen",
    )

    SetBothScreensWindowsColor = Symbol(
        [0x27D74],
        [0x2027D74],
        None,
        "Sets the palette of the frames of windows in both screens\n\nr0: palette"
        " index",
    )

    GetNotifyNote = Symbol(
        [0x487BC],
        [0x20487BC],
        None,
        "Returns the current value of NOTIFY_NOTE.\n\nreturn: bool",
    )

    SetNotifyNote = Symbol(
        [0x487CC], [0x20487CC], None, "Sets NOTIFY_NOTE to the given value.\n\nr0: bool"
    )

    InitMainTeamAfterQuiz = Symbol(
        [0x48AE0],
        [0x2048AE0],
        None,
        "Implements SPECIAL_PROC_INIT_MAIN_TEAM_AFTER_QUIZ (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x3 = Symbol(
        [0x48D28],
        [0x2048D28],
        None,
        "Implements SPECIAL_PROC_0x3 (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x4 = Symbol(
        [0x48DA0],
        [0x2048DA0],
        None,
        "Implements SPECIAL_PROC_0x4 (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    NoteSaveBase = Symbol(
        [0x492A0],
        [0x20492A0],
        None,
        "Probably related to saving or quicksaving?\n\nThis function prints the debug"
        " message 'NoteSave Base %d %d' with some values. It's also the only place"
        " where GetRngSeed is called.\n\nr0: possibly a flag/code that controls the"
        " type of save file to generate?\nothers: ?\nreturn: status code",
    )

    NoteLoadBase = Symbol(
        [0x496A8],
        [0x20496A8],
        None,
        "Probably related to loading a save file or quicksave?\n\nThis function prints"
        " the debug message 'NoteLoad Base %d' with some value. It's also the only"
        " place where SetRngSeed is called.\n\nreturn: status code",
    )

    GetGameMode = Symbol(
        [0x4B2F8],
        [0x204B2F8],
        None,
        "Gets the value of GAME_MODE.\n\nreturn: game mode",
    )

    InitScriptVariableValues = Symbol(
        [0x4B384],
        [0x204B384],
        None,
        "Initialize the script variable values table (SCRIPT_VARS_VALUES).\n\nThe whole"
        " table is first zero-initialized. Then, all script variable values are first"
        " initialized to their defaults, after which some of them are overwritten with"
        " other hard-coded values.\n\nNo params.",
    )

    InitEventFlagScriptVars = Symbol(
        [0x4B63C],
        [0x204B63C],
        None,
        "Initializes an assortment of event flag script variables (see the code for an"
        " exhaustive list).\n\nNo params.",
    )

    ZinitScriptVariable = Symbol(
        [0x4B76C],
        [0x204B76C],
        None,
        "Zero-initialize the values of the given script variable.\n\nr0: pointer to the"
        " local variable table (only needed if id >= VAR_LOCAL0)\nr1: script"
        " variable ID",
    )

    LoadScriptVariableRaw = Symbol(
        [0x4B7D4],
        [0x204B7D4],
        None,
        "Loads a script variable descriptor for a given ID.\n\nr0: [output] script"
        " variable descriptor pointer\nr1: pointer to the local variable table (doesn't"
        " need to be valid; just controls the output value pointer)\nr2: script"
        " variable ID",
    )

    LoadScriptVariableValue = Symbol(
        [0x4B824],
        [0x204B824],
        None,
        "Loads the value of a script variable.\n\nr0: pointer to the local variable"
        " table (only needed if id >= VAR_LOCAL0)\nr1: script variable ID\nreturn:"
        " value",
    )

    LoadScriptVariableValueAtIndex = Symbol(
        [0x4B9B0],
        [0x204B9B0],
        None,
        "Loads the value of a script variable at some index (for script variables that"
        " are arrays).\n\nr0: pointer to the local variable table (only needed if id >="
        " VAR_LOCAL0)\nr1: script variable ID\nr2: value index for the given script"
        " var\nreturn: value",
    )

    SaveScriptVariableValue = Symbol(
        [0x4BB58],
        [0x204BB58],
        None,
        "Saves the given value to a script variable.\n\nr0: pointer to local variable"
        " table (only needed if id >= VAR_LOCAL0)\nr1: script variable ID\nr2: value to"
        " save",
    )

    SaveScriptVariableValueAtIndex = Symbol(
        [0x4BCC0],
        [0x204BCC0],
        None,
        "Saves the given value to a script variable at some index (for script variables"
        " that are arrays).\n\nr0: pointer to local variable table (only needed if id"
        " >= VAR_LOCAL0)\nr1: script variable ID\nr2: value index for the given script"
        " var\nr3: value to save",
    )

    LoadScriptVariableValueSum = Symbol(
        [0x4BE38],
        [0x204BE38],
        None,
        "Loads the sum of all values of a given script variable (for script variables"
        " that are arrays).\n\nr0: pointer to the local variable table (only needed if"
        " id >= VAR_LOCAL0)\nr1: script variable ID\nreturn: sum of values",
    )

    LoadScriptVariableValueBytes = Symbol(
        [0x4BE9C],
        [0x204BE9C],
        None,
        "Loads some number of bytes from the value of a given script variable.\n\nr0:"
        " script variable ID\nr1: [output] script variable value bytes\nr2: number of"
        " bytes to load",
    )

    SaveScriptVariableValueBytes = Symbol(
        [0x4BF04],
        [0x204BF04],
        None,
        "Saves some number of bytes to the given script variable.\n\nr0: script"
        " variable ID\nr1: bytes to save\nr2: number of bytes",
    )

    ScriptVariablesEqual = Symbol(
        [0x4BF50],
        [0x204BF50],
        None,
        "Checks if two script variables have equal values. For arrays, compares"
        " elementwise for the length of the first variable.\n\nr0: pointer to the local"
        " variable table (only needed if id >= VAR_LOCAL0)\nr1: script variable ID"
        " 1\nr2: script variable ID 2\nreturn: true if values are equal, false"
        " otherwise",
    )

    EventFlagBackup = Symbol(
        [0x4C51C],
        [0x204C51C],
        None,
        "Saves event flag script variables (see the code for an exhaustive list) to"
        " their respective BACKUP script variables, but only in certain game"
        " modes.\n\nThis function prints the debug string 'EventFlag BackupGameMode %d'"
        " with the game mode.\n\nNo params.",
    )

    DumpScriptVariableValues = Symbol(
        [0x4C740],
        [0x204C740],
        None,
        "Runs EventFlagBackup, then copies the script variable values table"
        " (SCRIPT_VARS_VALUES) to the given pointer.\n\nr0: destination pointer for the"
        " data dump\nreturn: always 1",
    )

    RestoreScriptVariableValues = Symbol(
        [0x4C768],
        [0x204C768],
        None,
        "Restores the script variable values table (SCRIPT_VARS_VALUES) with the given"
        " data. The source data is assumed to be exactly 1024 bytes in length.\n\nr0:"
        " raw data to copy to the values table\nreturn: whether the restored value for"
        " VAR_VERSION is equal to its default value",
    )

    InitScenarioScriptVars = Symbol(
        [0x4C7C0],
        [0x204C7C0],
        None,
        "Initializes most of the SCENARIO_* script variables (except"
        " SCENARIO_TALK_BIT_FLAG for some reason). Also initializes the PLAY_OLD_GAME"
        " variable.\n\nNo params.",
    )

    SetScenarioScriptVar = Symbol(
        [0x4C950],
        [0x204C950],
        None,
        "Sets the given SCENARIO_* script variable with a given pair of values [val0,"
        " val1].\n\nIn the special case when the ID is VAR_SCENARIO_MAIN, and the set"
        " value is different from the old one, the REQUEST_CLEAR_COUNT script variable"
        " will be set to 0.\n\nr0: script variable ID\nr1: val0\nr2: val1",
    )

    GetSpecialEpisodeType = Symbol(
        [0x4CC24],
        [0x204CC24],
        None,
        "Gets the special episode type from the SPECIAL_EPISODE_TYPE script"
        " variable.\n\nreturn: special episode type",
    )

    ScenarioFlagBackup = Symbol(
        [0x4CFF0],
        [0x204CFF0],
        None,
        "Saves scenario flag script variables (SCENARIO_SELECT, SCENARIO_MAIN_BIT_FLAG)"
        " to their respective BACKUP script variables, but only in certain game"
        " modes.\n\nThis function prints the debug string 'ScenarioFlag BackupGameMode"
        " %d' with the game mode.\n\nNo params.",
    )

    InitWorldMapScriptVars = Symbol(
        [0x4D0C0],
        [0x204D0C0],
        None,
        "Initializes the WORLD_MAP_* script variable values (IDs 0x55-0x57).\n\nNo"
        " params.",
    )

    InitDungeonListScriptVars = Symbol(
        [0x4D1C8],
        [0x204D1C8],
        None,
        "Initializes the DUNGEON_*_LIST script variable values (IDs 0x4f-0x54).\n\nNo"
        " params.",
    )

    SetDungeonTipShown = Symbol(
        [0x4D588],
        [0x204D588],
        None,
        "Marks a dungeon tip as already shown to the player\n\nr0: Dungeon tip ID",
    )

    GetDungeonTipShown = Symbol(
        [0x4D5C8],
        [0x204D5C8],
        None,
        "Checks if a dungeon tip has already been shown before or not.\n\nr0: Dungeon"
        " tip ID\nreturn: True if the tip has been shown before, false otherwise.",
    )

    MonsterSpawnsEnabled = Symbol(
        [0x4D698],
        [0x204D698],
        None,
        "Always returns true.\n\nThis function seems to be a debug switch that the"
        " developers may have used to disable the random enemy spawn. \nIf it returned"
        " false, the call to SpawnMonster inside TrySpawnMonsterAndTickSpawnCounter"
        " would not be executed.\n\nreturn: bool (always true)",
    )

    SetAdventureLogStructLocation = Symbol(
        [0x4FD5C],
        [0x204FD5C],
        None,
        "Sets the location of the adventure log struct in memory.\n\nSets it in a"
        " static memory location (At 0x22AB69C [US], 0x22ABFDC [EU], 0x22ACE58"
        " [JP])\n\nNo params.",
    )

    SetAdventureLogDungeonFloor = Symbol(
        [0x4FD74],
        [0x204FD74],
        None,
        "Sets the current dungeon floor pair.\n\nr0: struct dungeon_floor_pair",
    )

    GetAdventureLogDungeonFloor = Symbol(
        [0x4FD94],
        [0x204FD94],
        None,
        "Gets the current dungeon floor pair.\n\nreturn: struct dungeon_floor_pair",
    )

    ClearAdventureLogStruct = Symbol(
        [0x4FDA8],
        [0x204FDA8],
        None,
        "Clears the adventure log structure.\n\nNo params.",
    )

    SetAdventureLogCompleted = Symbol(
        [0x4FED4],
        [0x204FED4],
        None,
        "Marks one of the adventure log entry as completed.\n\nr0: entry ID",
    )

    IsAdventureLogNotEmpty = Symbol(
        [0x4FEFC],
        [0x204FEFC],
        None,
        "Checks if at least one of the adventure log entry is completed.\n\nreturn:"
        " bool",
    )

    GetAdventureLogCompleted = Symbol(
        [0x4FF34],
        [0x204FF34],
        None,
        "Checks if one adventure log entry is completed.\n\nr0: entry ID\nreturn: bool",
    )

    IncrementNbDungeonsCleared = Symbol(
        [0x4FF60],
        [0x204FF60],
        None,
        "Increments by 1 the number of dungeons cleared.\n\nImplements"
        " SPECIAL_PROC_0x3A (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    GetNbDungeonsCleared = Symbol(
        [0x4FFA4],
        [0x204FFA4],
        None,
        "Gets the number of dungeons cleared.\n\nreturn: the number of dungeons"
        " cleared",
    )

    IncrementNbFriendRescues = Symbol(
        [0x4FFB8],
        [0x204FFB8],
        None,
        "Increments by 1 the number of successful friend rescues.\n\nNo params.",
    )

    GetNbFriendRescues = Symbol(
        [0x50000],
        [0x2050000],
        None,
        "Gets the number of successful friend rescues.\n\nreturn: the number of"
        " successful friend rescues",
    )

    IncrementNbEvolutions = Symbol(
        [0x50014],
        [0x2050014],
        None,
        "Increments by 1 the number of evolutions.\n\nNo params.",
    )

    GetNbEvolutions = Symbol(
        [0x5005C],
        [0x205005C],
        None,
        "Gets the number of evolutions.\n\nreturn: the number of evolutions",
    )

    IncrementNbSteals = Symbol(
        [0x50070],
        [0x2050070],
        None,
        "Leftover from Time & Darkness. Does not do anything.\n\nCalls to this matches"
        " the ones for incrementing the number of successful steals in Time &"
        " Darkness.\n\nNo params.",
    )

    IncrementNbEggsHatched = Symbol(
        [0x50074],
        [0x2050074],
        None,
        "Increments by 1 the number of eggs hatched.\n\nNo params.",
    )

    GetNbEggsHatched = Symbol(
        [0x500B0],
        [0x20500B0],
        None,
        "Gets the number of eggs hatched.\n\nreturn: the number of eggs hatched",
    )

    GetNbPokemonJoined = Symbol(
        [0x500C4],
        [0x20500C4],
        None,
        "Gets the number of different pokémon that joined.\n\nreturn: the number of"
        " different pokémon that joined",
    )

    GetNbMovesLearned = Symbol(
        [0x500D8],
        [0x20500D8],
        None,
        "Gets the number of different moves learned.\n\nreturn: the number of different"
        " moves learned",
    )

    SetVictoriesOnOneFloor = Symbol(
        [0x500EC],
        [0x20500EC],
        None,
        "Sets the record of victories on one floor.\n\nr0: the new record of victories",
    )

    GetVictoriesOnOneFloor = Symbol(
        [0x50120],
        [0x2050120],
        None,
        "Gets the record of victories on one floor.\n\nreturn: the record of victories",
    )

    SetPokemonJoined = Symbol(
        [0x50134], [0x2050134], None, "Marks one pokémon as joined.\n\nr0: monster ID"
    )

    SetPokemonBattled = Symbol(
        [0x50190], [0x2050190], None, "Marks one pokémon as battled.\n\nr0: monster ID"
    )

    GetNbPokemonBattled = Symbol(
        [0x501EC],
        [0x20501EC],
        None,
        "Gets the number of different pokémon that battled against you.\n\nreturn: the"
        " number of different pokémon that battled against you",
    )

    IncrementNbBigTreasureWins = Symbol(
        [0x50200],
        [0x2050200],
        None,
        "Increments by 1 the number of big treasure wins.\n\nImplements"
        " SPECIAL_PROC_0x3B (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    SetNbBigTreasureWins = Symbol(
        [0x50220],
        [0x2050220],
        None,
        "Sets the number of big treasure wins.\n\nr0: the new number of big treasure"
        " wins",
    )

    GetNbBigTreasureWins = Symbol(
        [0x50258],
        [0x2050258],
        None,
        "Gets the number of big treasure wins.\n\nreturn: the number of big treasure"
        " wins",
    )

    SetNbRecycled = Symbol(
        [0x5026C],
        [0x205026C],
        None,
        "Sets the number of items recycled.\n\nr0: the new number of items recycled",
    )

    GetNbRecycled = Symbol(
        [0x502A4],
        [0x20502A4],
        None,
        "Gets the number of items recycled.\n\nreturn: the number of items recycled",
    )

    IncrementNbSkyGiftsSent = Symbol(
        [0x502B8],
        [0x20502B8],
        None,
        "Increments by 1 the number of sky gifts sent.\n\nImplements"
        " SPECIAL_PROC_SEND_SKY_GIFT_TO_GUILDMASTER (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    SetNbSkyGiftsSent = Symbol(
        [0x502D8],
        [0x20502D8],
        None,
        "Sets the number of Sky Gifts sent.\n\nreturn: the number of Sky Gifts sent",
    )

    GetNbSkyGiftsSent = Symbol(
        [0x50310],
        [0x2050310],
        None,
        "Gets the number of Sky Gifts sent.\n\nreturn: the number of Sky Gifts sent",
    )

    ComputeSpecialCounters = Symbol(
        [0x50324],
        [0x2050324],
        None,
        "Computes the counters from the bit fields in the adventure log, as they are"
        " not updated automatically when bit fields are altered.\n\nAffects"
        " GetNbPokemonJoined, GetNbMovesLearned, GetNbPokemonBattled and"
        " GetNbItemAcquired.\n\nNo params.",
    )

    RecruitSpecialPokemonLog = Symbol(
        [0x5057C],
        [0x205057C],
        None,
        "Marks a specified special pokémon as recruited in the adventure log.\n\nr0:"
        " monster ID",
    )

    IncrementNbFainted = Symbol(
        [0x505E8],
        [0x20505E8],
        None,
        "Increments by 1 the number of times you fainted.\n\nNo params.",
    )

    GetNbFainted = Symbol(
        [0x50624],
        [0x2050624],
        None,
        "Gets the number of times you fainted.\n\nreturn: the number of times you"
        " fainted",
    )

    SetItemAcquired = Symbol(
        [0x50638],
        [0x2050638],
        None,
        "Marks one specific item as acquired.\n\nr0: item ID",
    )

    GetNbItemAcquired = Symbol(
        [0x50704],
        [0x2050704],
        None,
        "Gets the number of items acquired.\n\nreturn: the number of items acquired",
    )

    SetChallengeLetterCleared = Symbol(
        [0x50758],
        [0x2050758],
        None,
        "Sets a challenge letter as cleared.\n\nr0: challenge ID",
    )

    GetSentryDutyGamePoints = Symbol(
        [0x507DC],
        [0x20507DC],
        None,
        "Gets the points for the associated rank in the footprints minigame.\n\nr0: the"
        " rank (range 0-4, 1st to 5th)\nreturn: points",
    )

    SetSentryDutyGamePoints = Symbol(
        [0x507F4],
        [0x20507F4],
        None,
        "Sets a new record in the footprints minigame.\n\nr0: points\nreturn: the rank"
        " (range 0-4, 1st to 5th; -1 if out of ranking)",
    )

    SubFixedPoint = Symbol(
        [0x51248],
        [0x2051248],
        None,
        "Compute the subtraction of two decimal fixed-point numbers (16 fraction"
        " bits).\n\nFloats are in the format {16-bit integer part, 16-bit thousandths},"
        " where the integer part is the lower word. Probably used primarily for"
        " belly.\n\nr0: float\nr1: decrement\nreturn: max(float - decrement, 0)",
    )

    BinToDecFixedPoint = Symbol(
        [0x51358],
        [0x2051358],
        None,
        "Convert a binary fixed-point number (16 fraction bits) to the decimal"
        " fixed-point number (16 fraction bits) used for belly calculations."
        " Thousandths are floored.\n\nIf <data> holds the raw binary data, a binary"
        " fixed-point number (16 fraction bits) has the value ((unsigned)data) *"
        " 2^-16), and the decimal fixed-point number (16 fraction bits) used for belly"
        " has the value (data & 0xffff) + (data >> 16)/1000.\n\nr0: pointer p, where"
        " ((const unsigned *)p)[1] is the fractional number in binary fixed-point"
        " format to convert\nreturn: fractional number in decimal fixed-point format",
    )

    CeilFixedPoint = Symbol(
        [0x5139C],
        [0x205139C],
        None,
        "Compute the ceiling of a decimal fixed-point number (16 fraction"
        " bits).\n\nFloats are in the format {16-bit integer part, 16-bit thousandths},"
        " where the integer part is the lower word. Probably used primarily for"
        " belly.\n\nr0: float\nreturn: ceil(float)",
    )

    DungeonGoesUp = Symbol(
        [0x515C0],
        [0x20515C0],
        None,
        "Returns whether the specified dungeon is considered as going upward or"
        " not\n\nr0: dungeon id\nreturn: bool",
    )

    GetMaxRescueAttempts = Symbol(
        [0x516B8],
        [0x20516B8],
        None,
        "Returns the maximum rescue attempts allowed in the specified dungeon.\n\nr0:"
        " dungeon id\nreturn: Max rescue attempts, or -1 if rescues are disabled.",
    )

    JoinedAtRangeCheck = Symbol(
        [0x517C8],
        [0x20517C8],
        None,
        "Returns whether a certain joined_at field value is between"
        " dungeon_id::DUNGEON_JOINED_AT_BIDOOF and"
        " dungeon_id::DUNGEON_DUMMY_0xE3.\n\nr0: joined_at id\nreturn: bool",
    )

    JoinedAtRangeCheck2 = Symbol(
        [0x51A98],
        [0x2051A98],
        None,
        "Returns whether a certain joined_at field value is equal to"
        " dungeon_id::DUNGEON_BEACH or is between dungeon_id::DUNGEON_DUMMY_0xEC and"
        " dungeon_id::DUNGEON_DUMMY_0xF0.\n\nr0: joined_at id\nreturn: bool",
    )

    GetMonsterGender = Symbol(
        [0x52AE0],
        [0x2052AE0],
        None,
        "Returns the gender field of a monster given its ID.\n\nr0: monster id\nreturn:"
        " monster gender",
    )

    GetSpriteSize = Symbol(
        [0x52B18],
        [0x2052B18],
        None,
        "Returns the sprite size of the specified monster. If the size is between 1 and"
        " 6, 6 will be returned.\n\nr0: monster id\nreturn: sprite size",
    )

    GetSpriteFileSize = Symbol(
        [0x52B54],
        [0x2052B54],
        None,
        "Returns the sprite file size of the specified monster.\n\nr0: monster"
        " id\nreturn: sprite file size",
    )

    GetCanMoveFlag = Symbol(
        [0x52BEC],
        [0x2052BEC],
        None,
        "Returns the flag that determines if a monster can move in dungeons.\n\nr0:"
        " Monster ID\nreturn: 'Can move' flag",
    )

    GetMonsterPreEvolution = Symbol(
        [0x52CE0],
        [0x2052CE0],
        None,
        "Returns the pre-evolution id of a monster given its ID.\n\nr0: monster"
        " id\nreturn: ID of the monster that evolves into the one specified in r0",
    )

    GetEvolutions = Symbol(
        [0x54204],
        [0x2054204],
        None,
        "Returns a list of all the possible evolutions for a given monster id.\n\nr0:"
        " Monster id\nr1: [Output] Array that will hold the list of monster ids the"
        " specified monster can evolve into\nr2: True to skip the check that prevents"
        " returning monsters with a different sprite size than the current one\nr3:"
        " True to skip the check that prevents Shedinja from being counted as a"
        " potential evolution\nreturn: Number of possible evolutions for the specified"
        " monster id",
    )

    GetMonsterIdFromSpawnEntry = Symbol(
        [0x547FC],
        [0x20547FC],
        None,
        "Returns the monster ID of the specified monster spawn entry\n\nr0: Pointer to"
        " the monster spawn entry\nreturn: monster_spawn_entry::id",
    )

    GetMonsterLevelFromSpawnEntry = Symbol(
        [0x54834],
        [0x2054834],
        None,
        "Returns the level of the specified monster spawn entry.\n\nr0: pointer to the"
        " monster spawn entry\nreturn: uint8_t",
    )

    GetMonsterGenderVeneer = Symbol(
        [0x54ADC],
        [0x2054ADC],
        None,
        "Likely a linker-generated veneer for GetMonsterGender.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nr0:"
        " monster id\nreturn: monster gender",
    )

    IsUnown = Symbol(
        [0x54E04],
        [0x2054E04],
        None,
        "Checks if a monster ID is an Unown.\n\nr0: monster ID\nreturn: bool",
    )

    IsShaymin = Symbol(
        [0x54E20],
        [0x2054E20],
        None,
        "Checks if a monster ID is a Shaymin form.\n\nr0: monster ID\nreturn: bool",
    )

    IsCastform = Symbol(
        [0x54E50],
        [0x2054E50],
        None,
        "Checks if a monster ID is a Castform form.\n\nr0: monster ID\nreturn: bool",
    )

    IsCherrim = Symbol(
        [0x54EA8],
        [0x2054EA8],
        None,
        "Checks if a monster ID is a Cherrim form.\n\nr0: monster ID\nreturn: bool",
    )

    IsDeoxys = Symbol(
        [0x54EF0],
        [0x2054EF0],
        None,
        "Checks if a monster ID is a Deoxys form.\n\nr0: monster ID\nreturn: bool",
    )

    IsMonsterOnTeam = Symbol(
        [0x554C4],
        [0x20554C4],
        None,
        "Checks if a given monster is on the exploration team (not necessarily the"
        " active party)?\n\nr0: monster ID\nr1: ?\nreturn: bool",
    )

    CheckTeamMemberField8 = Symbol(
        [0x565E0],
        [0x20565E0],
        None,
        "Checks if a value obtained from team_member::field_0x8 is equal to certain"
        " values.\n\nThis is known to return true for some or all of the guest"
        " monsters.\n\nr0: Value read from team_member::field_0x8\nreturn: True if the"
        " value is equal to 0x55AA or 0x5AA5",
    )

    GetTeamMemberData = Symbol(
        [0x56708],
        [0x2056708],
        None,
        "Returns a struct containing information about a team member.\n\nr0:"
        " Index\nreturn: Pointer to struct containing team member information",
    )

    SetTeamSetupHeroAndPartnerOnly = Symbol(
        [0x56D48],
        [0x2056D48],
        None,
        "Implements SPECIAL_PROC_SET_TEAM_SETUP_HERO_AND_PARTNER_ONLY (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    SetTeamSetupHeroOnly = Symbol(
        [0x56E2C],
        [0x2056E2C],
        None,
        "Implements SPECIAL_PROC_SET_TEAM_SETUP_HERO_ONLY (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    GetPartyMembers = Symbol(
        [0x56F9C],
        [0x2056F9C],
        None,
        "Appears to get the team's active party members. Implements most of"
        " SPECIAL_PROC_IS_TEAM_SETUP_SOLO (see ScriptSpecialProcessCall).\n\nr0:"
        " [output] Array of 4 2-byte values (they seem to be indexes of some sort)"
        " describing each party member, which will be filled in by the function. The"
        " input can be a null pointer if the party members aren't needed\nreturn:"
        " Number of party members",
    )

    IqSkillFlagTest = Symbol(
        [0x59280],
        [0x2059280],
        None,
        "Tests whether an IQ skill with a given ID is active.\n\nr0: IQ skill bitvector"
        " to test\nr1: IQ skill ID\nreturn: bool",
    )

    GetExplorerMazeMonster = Symbol(
        [0x59474],
        [0x2059474],
        None,
        "Returns the data of a monster sent into the Explorer Dojo using the 'exchange"
        " teams' option.\n\nr0: Entry number (0-3)\nreturn: Ground monster data of the"
        " specified entry",
    )

    GetSosMailCount = Symbol(
        [0x5BCF8],
        [0x205BCF8],
        None,
        "Implements SPECIAL_PROC_GET_SOS_MAIL_COUNT (see"
        " ScriptSpecialProcessCall).\n\nr0: ?\nr1: some flag?\nreturn: SOS mail count",
    )

    DungeonRequestsDone = Symbol(
        [0x5F120],
        [0x205F120],
        None,
        "Seems to return the number of missions completed.\n\nPart of the"
        " implementation for SPECIAL_PROC_DUNGEON_HAD_REQUEST_DONE (see"
        " ScriptSpecialProcessCall).\n\nr0: ?\nr1: some flag?\nreturn: number of"
        " missions completed",
    )

    DungeonRequestsDoneWrapper = Symbol(
        [0x5F18C],
        [0x205F18C],
        None,
        "Calls DungeonRequestsDone with the second argument set to false.\n\nr0:"
        " ?\nreturn: number of mission completed",
    )

    AnyDungeonRequestsDone = Symbol(
        [0x5F19C],
        [0x205F19C],
        None,
        "Calls DungeonRequestsDone with the second argument set to true, and converts"
        " the integer output to a boolean.\n\nr0: ?\nreturn: bool: whether the number"
        " of missions completed is greater than 0",
    )

    ScriptSpecialProcess0x3D = Symbol(
        [0x65ECC],
        [0x2065ECC],
        None,
        "Implements SPECIAL_PROC_0x3D (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x3E = Symbol(
        [0x65EDC],
        [0x2065EDC],
        None,
        "Implements SPECIAL_PROC_0x3E (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x17 = Symbol(
        [0x65FC4],
        [0x2065FC4],
        None,
        "Implements SPECIAL_PROC_0x17 (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ItemAtTableIdx = Symbol(
        [0x66074],
        [0x2066074],
        None,
        "Gets info about the item at a given item table (not sure what this table"
        " is...) index.\n\nUsed by SPECIAL_PROC_COUNT_TABLE_ITEM_TYPE_IN_BAG and"
        " friends (see ScriptSpecialProcessCall).\n\nr0: table index\nr1: [output]"
        " pointer to an owned_item",
    )

    WaitForInterrupt = Symbol(
        [0x7BFC8],
        [0x207BFC8],
        None,
        "Presumably blocks until the program receives an interrupt.\n\nThis just calls"
        " (in Ghidra terminology) coproc_moveto_Wait_for_interrupt(0). See"
        " https://en.wikipedia.org/wiki/ARM_architecture_family#Coprocessors.\n\nNo"
        " params.",
    )

    FileInit = Symbol(
        [0x7F77C],
        [0x207F77C],
        None,
        "Initializes a file_stream structure for file I/O.\n\nThis function must always"
        " be called before opening a file.\n\nr0: file_stream pointer",
    )

    Abs = Symbol(
        [0x868F4],
        [0x20868F4],
        None,
        "Takes the absolute value of an integer.\n\nr0: x\nreturn: abs(x)",
    )

    Mbtowc = Symbol(
        [0x87554],
        [0x2087554],
        None,
        "The mbtowc(3) C library function.\n\nr0: pwc\nr1: s\nr2: n\nreturn: number of"
        " consumed bytes, or -1 on failure",
    )

    TryAssignByte = Symbol(
        [0x8758C],
        [0x208758C],
        None,
        "Assign a byte to the target of a pointer if the pointer is non-null.\n\nr0:"
        " pointer\nr1: value\nreturn: true on success, false on failure",
    )

    TryAssignByteWrapper = Symbol(
        [0x875A0],
        [0x20875A0],
        None,
        "Wrapper around TryAssignByte.\n\nAccesses the TryAssignByte function with a"
        " weird chain of pointer dereferences.\n\nr0: pointer\nr1: value\nreturn: true"
        " on success, false on failure",
    )

    Wcstombs = Symbol(
        [0x875BC],
        [0x20875BC],
        None,
        "The wcstombs(3) C library function.\n\nr0: dest\nr1: src\nr2: n\nreturn:"
        " characters converted",
    )

    Memcpy = Symbol(
        [0x87634],
        [0x2087634],
        None,
        "The memcpy(3) C library function.\n\nr0: dest\nr1: src\nr2: n",
    )

    Memmove = Symbol(
        [0x87654],
        [0x2087654],
        None,
        "The memmove(3) C library function.\n\nThe implementation is nearly the same as"
        " Memcpy, but it copies bytes from back to front if src < dst.\n\nr0: dest\nr1:"
        " src\nr2: n",
    )

    Memset = Symbol(
        [0x876A0],
        [0x20876A0],
        None,
        "The memset(3) C library function.\n\nThis is just a wrapper around"
        " MemsetInternal that returns the pointer at the end.\n\nr0: s\nr1: c (int, but"
        " must be a single-byte value)\nr2: n\nreturn: s",
    )

    Memchr = Symbol(
        [0x876B4],
        [0x20876B4],
        None,
        "The memchr(3) C library function.\n\nr0: s\nr1: c\nr2: n\nreturn: pointer to"
        " first occurrence of c in s, or a null pointer if no match",
    )

    Memcmp = Symbol(
        [0x876E0],
        [0x20876E0],
        None,
        "The memcmp(3) C library function.\n\nr0: s1\nr1: s2\nr2: n\nreturn: comparison"
        " value",
    )

    MemsetInternal = Symbol(
        [0x87720],
        [0x2087720],
        None,
        "The actual memory-setting implementation for the memset(3) C library"
        " function.\n\nThis function is optimized to set bytes in 4-byte chunks for n"
        " >= 32, correctly handling any unaligned bytes at the front/back. In this"
        " case, it also further optimizes by unrolling a for loop to set 8 4-byte"
        " values at once (effectively a 32-byte chunk).\n\nr0: s\nr1: c (int, but must"
        " be a single-byte value)\nr2: n",
    )

    VsprintfInternalSlice = Symbol(
        [0x8900C],
        [0x208900C],
        None,
        "This is what implements the bulk of VsprintfInternal.\n\nThe"
        " __vsprintf_internal in the modern-day version of glibc relies on"
        " __vfprintf_internal; this function has a slightly different interface, but it"
        " serves a similar role.\n\nr0: function pointer to append to the string being"
        " built (VsprintfInternal uses TryAppendToSlice)\nr1: string buffer slice\nr2:"
        " format\nr3: ap\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    TryAppendToSlice = Symbol(
        [0x89830],
        [0x2089830],
        None,
        "Best-effort append the given data to a slice. If the slice's capacity is"
        " reached, any remaining data will be truncated.\n\nr0: slice pointer\nr1:"
        " buffer of data to append\nr2: number of bytes in the data buffer\nreturn:"
        " true",
    )

    VsprintfInternal = Symbol(
        [0x89874],
        [0x2089874],
        None,
        "This is what implements Vsprintf. It's akin to __vsprintf_internal in the"
        " modern-day version of glibc (in fact, it's probably an older version of"
        " this).\n\nr0: str\nr1: maxlen (Vsprintf passes UINT32_MAX for this)\nr2:"
        " format\nr3: ap\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    Vsprintf = Symbol(
        [0x898DC],
        [0x20898DC],
        None,
        "The vsprintf(3) C library function.\n\nr0: str\nr1: format\nr2: ap\nreturn:"
        " number of characters printed, excluding the null-terminator",
    )

    Snprintf = Symbol(
        [0x898F4],
        [0x20898F4],
        None,
        "The snprintf(3) C library function.\n\nThis calls VsprintfInternal directly,"
        " so it's presumably the real snprintf.\n\nr0: str\nr1: n\nr2: format\n...:"
        " variadic\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    Sprintf = Symbol(
        [0x8991C],
        [0x208991C],
        None,
        "The sprintf(3) C library function.\n\nThis calls VsprintfInternal directly, so"
        " it's presumably the real sprintf.\n\nr0: str\nr1: format\n...:"
        " variadic\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    Strlen = Symbol(
        [0x89A10],
        [0x2089A10],
        None,
        "The strlen(3) C library function.\n\nr0: s\nreturn: length of s",
    )

    Strcpy = Symbol(
        [0x89A2C],
        [0x2089A2C],
        None,
        "The strcpy(3) C library function.\n\nThis function is optimized to copy"
        " characters in aligned 4-byte chunks if possible, correctly handling any"
        " unaligned bytes at the front/back.\n\nr0: dest\nr1: src",
    )

    Strncpy = Symbol(
        [0x89AF4],
        [0x2089AF4],
        None,
        "The strncpy(3) C library function.\n\nr0: dest\nr1: src\nr2: n",
    )

    Strcat = Symbol(
        [0x89B44],
        [0x2089B44],
        None,
        "The strcat(3) C library function.\n\nr0: dest\nr1: src",
    )

    Strncat = Symbol(
        [0x89B74],
        [0x2089B74],
        None,
        "The strncat(3) C library function.\n\nr0: dest\nr1: src\nr2: n",
    )

    Strcmp = Symbol(
        [0x89BC4],
        [0x2089BC4],
        None,
        "The strcmp(3) C library function.\n\nSimilarly to Strcpy, this function is"
        " optimized to compare characters in aligned 4-byte chunks if possible.\n\nr0:"
        " s1\nr1: s2\nreturn: comparison value",
    )

    Strncmp = Symbol(
        [0x89CD8],
        [0x2089CD8],
        None,
        "The strncmp(3) C library function.\n\nr0: s1\nr1: s2\nr2: n\nreturn:"
        " comparison value",
    )

    Strchr = Symbol(
        [0x89D0C],
        [0x2089D0C],
        None,
        "The strchr(3) C library function.\n\nr0: string\nr1: c\nreturn: pointer to the"
        " located byte c, or null pointer if no match",
    )

    Strcspn = Symbol(
        [0x89D48],
        [0x2089D48],
        None,
        "The strcspn(3) C library function.\n\nr0: string\nr1: stopset\nreturn: offset"
        " of the first character in string within stopset",
    )

    Strstr = Symbol(
        [0x89E08],
        [0x2089E08],
        None,
        "The strstr(3) C library function.\n\nr0: haystack\nr1: needle\nreturn: pointer"
        " into haystack where needle starts, or null pointer if no match",
    )

    Wcslen = Symbol(
        [0x8B780],
        [0x208B780],
        None,
        "The wcslen(3) C library function.\n\nr0: ws\nreturn: length of ws",
    )

    AddFloat = Symbol(
        [0x8F050],
        [0x208F050],
        None,
        "This appears to be the libgcc implementation of __addsf3 (not sure which gcc"
        " version), which implements the addition operator for IEEE 754 floating-point"
        " numbers.\n\nr0: a\nr1: b\nreturn: a + b",
    )

    DivideFloat = Symbol(
        [0x8F5CC],
        [0x208F5CC],
        None,
        "This appears to be the libgcc implementation of __divsf3 (not sure which gcc"
        " version), which implements the division operator for IEEE 754 floating-point"
        " numbers.\n\nr0: dividend\nr1: divisor\nreturn: dividend / divisor",
    )

    FloatToDouble = Symbol(
        [0x8F984],
        [0x208F984],
        None,
        "This appears to be the libgcc implementation of __extendsfdf2 (not sure which"
        " gcc version), which implements the float to double cast operation for IEEE"
        " 754 floating-point numbers.\n\nr0: float\nreturn: (double)float",
    )

    FloatToInt = Symbol(
        [0x8FA08],
        [0x208FA08],
        None,
        "This appears to be the libgcc implementation of __fixsfsi (not sure which gcc"
        " version), which implements the float to int cast operation for IEEE 754"
        " floating-point numbers. The output saturates if the input is out of the"
        " representable range for the int type.\n\nr0: float\nreturn: (int)float",
    )

    IntToFloat = Symbol(
        [0x8FA3C],
        [0x208FA3C],
        None,
        "This appears to be the libgcc implementation of __floatsisf (not sure which"
        " gcc version), which implements the int to float cast operation for IEEE 754"
        " floating-point numbers.\n\nr0: int\nreturn: (float)int",
    )

    UIntToFloat = Symbol(
        [0x8FA84],
        [0x208FA84],
        None,
        "This appears to be the libgcc implementation of __floatunsisf (not sure which"
        " gcc version), which implements the unsigned int to float cast operation for"
        " IEEE 754 floating-point numbers.\n\nr0: uint\nreturn: (float)uint",
    )

    MultiplyFloat = Symbol(
        [0x8FACC],
        [0x208FACC],
        None,
        "This appears to be the libgcc implementation of __mulsf3 (not sure which gcc"
        " version), which implements the multiplication operator for IEEE 754"
        " floating-point numbers.",
    )

    Sqrtf = Symbol(
        [0x8FCAC],
        [0x208FCAC],
        None,
        "The sqrtf(3) C library function.\n\nr0: x\nreturn: sqrt(x)",
    )

    SubtractFloat = Symbol(
        [0x8FD9C],
        [0x208FD9C],
        None,
        "This appears to be the libgcc implementation of __subsf3 (not sure which gcc"
        " version), which implements the subtraction operator for IEEE 754"
        " floating-point numbers.\n\nr0: a\nr1: b\nreturn: a - b",
    )

    DivideInt = Symbol(
        [0x9023C],
        [0x209023C],
        None,
        "This appears to be the libgcc implementation of __divsi3 (not sure which gcc"
        " version), which implements the division operator for signed ints.\n\nThe"
        " return value is a 64-bit integer, with the quotient (dividend / divisor) in"
        " the lower 32 bits and the remainder (dividend % divisor) in the upper 32"
        " bits. In accordance with the Procedure Call Standard for the Arm Architecture"
        " (see"
        " https://github.com/ARM-software/abi-aa/blob/60a8eb8c55e999d74dac5e368fc9d7e36e38dda4/aapcs32/aapcs32.rst#result-return),"
        " this means that the quotient is returned in r0 and the remainder is returned"
        " in r1.\n\nr0: dividend\nr1: divisor\nreturn: (quotient) | (remainder << 32)",
    )

    DivideUInt = Symbol(
        [0x90448],
        [0x2090448],
        None,
        "This appears to be the libgcc implementation of __udivsi3 (not sure which gcc"
        " version), which implements the division operator for unsigned ints.\n\nThe"
        " return value is a 64-bit integer, with the quotient (dividend / divisor) in"
        " the lower 32 bits and the remainder (dividend % divisor) in the upper 32"
        " bits. In accordance with the Procedure Call Standard for the Arm Architecture"
        " (see"
        " https://github.com/ARM-software/abi-aa/blob/60a8eb8c55e999d74dac5e368fc9d7e36e38dda4/aapcs32/aapcs32.rst#result-return),"
        " this means that the quotient is returned in r0 and the remainder is returned"
        " in r1.\nNote: This function falls through to DivideUIntNoZeroCheck.\n\nr0:"
        " dividend\nr1: divisor\nreturn: (quotient) | (remainder << 32)",
    )

    DivideUIntNoZeroCheck = Symbol(
        [0x90450],
        [0x2090450],
        None,
        "Subsidiary function to DivideUInt. Skips the initial check for divisor =="
        " 0.\n\nThe return value is a 64-bit integer, with the quotient (dividend /"
        " divisor) in the lower 32 bits and the remainder (dividend % divisor) in the"
        " upper 32 bits. In accordance with the Procedure Call Standard for the Arm"
        " Architecture (see"
        " https://github.com/ARM-software/abi-aa/blob/60a8eb8c55e999d74dac5e368fc9d7e36e38dda4/aapcs32/aapcs32.rst#result-return),"
        " this means that the quotient is returned in r0 and the remainder is returned"
        " in r1.\nThis function appears to only be called internally.\n\nr0:"
        " dividend\nr1: divisor\nreturn: (quotient) | (remainder << 32)",
    )


class EuArm9Data:
    JUICE_BAR_NECTAR_IQ_GAIN = Symbol(
        [0x118B8], [0x20118B8], 0x1, "IQ gain when ingesting nectar at the Juice Bar."
    )

    TEXT_SPEED = Symbol([0x20DF0], [0x2020DF0], None, "Controls text speed.")

    HERO_START_LEVEL = Symbol(
        [0x48B9C], [0x2048B9C], None, "Starting level of the hero."
    )

    PARTNER_START_LEVEL = Symbol(
        [0x48C0C], [0x2048C0C], None, "Starting level of the partner."
    )

    DEFAULT_MEMORY_ARENA_SIZE = Symbol(
        [0xE58],
        [0x2000E58],
        0x4,
        "Length in bytes of the default memory allocation arena, 1991680.",
    )

    AURA_BOW_ID_LAST = Symbol(
        [0xCCBC], [0x200CCBC], 0x4, "Highest item ID of the aura bows."
    )

    NUMBER_OF_ITEMS = Symbol([0xE930], [0x200E930], 0x4, "Number of items in the game.")

    MAX_MONEY_CARRIED = Symbol(
        [0xEDF8],
        [0x200EDF8],
        0x4,
        "Maximum amount of money the player can carry, 99999.",
    )

    MAX_MONEY_STORED = Symbol(
        [0x107F8],
        [0x20107F8],
        0x4,
        "Maximum amount of money the player can store in the Duskull Bank, 9999999.",
    )

    SCRIPT_VARS_VALUES_PTR = Symbol(
        [0x4B630, 0x4B81C, 0x4C764, 0x4C7BC],
        [0x204B630, 0x204B81C, 0x204C764, 0x204C7BC],
        0x4,
        "Hard-coded pointer to SCRIPT_VARS_VALUES.",
    )

    MONSTER_ID_LIMIT = Symbol(
        [0x54818],
        [0x2054818],
        0x4,
        "One more than the maximum valid monster ID (0x483).",
    )

    MAX_RECRUITABLE_TEAM_MEMBERS = Symbol(
        [0x555B4, 0x559C8],
        [0x20555B4, 0x20559C8],
        None,
        "555, appears to be the maximum number of members recruited to an exploration"
        " team, at least for the purposes of some checks that need to iterate over all"
        " team members.",
    )

    CART_REMOVED_IMG_DATA = Symbol([0x92EE4], [0x2092EE4], 0x2000, "")

    EXCLUSIVE_ITEM_STAT_BOOST_DATA = Symbol(
        [0x9852C],
        [0x209852C],
        0x3C,
        "Contains stat boost effects for different exclusive item classes.\n\nEach"
        " 4-byte entry contains the boost data for (attack, special attack, defense,"
        " special defense), 1 byte each, for a specific exclusive item class, indexed"
        " according to the stat boost data index list.",
    )

    EXCLUSIVE_ITEM_ATTACK_BOOSTS = Symbol(
        [0x9852C], [0x209852C], 0x39, "EXCLUSIVE_ITEM_STAT_BOOST_DATA, offset by 0"
    )

    EXCLUSIVE_ITEM_SPECIAL_ATTACK_BOOSTS = Symbol(
        [0x9852D], [0x209852D], 0x39, "EXCLUSIVE_ITEM_STAT_BOOST_DATA, offset by 1"
    )

    EXCLUSIVE_ITEM_DEFENSE_BOOSTS = Symbol(
        [0x9852E], [0x209852E], 0x39, "EXCLUSIVE_ITEM_STAT_BOOST_DATA, offset by 2"
    )

    EXCLUSIVE_ITEM_SPECIAL_DEFENSE_BOOSTS = Symbol(
        [0x9852F], [0x209852F], 0x39, "EXCLUSIVE_ITEM_STAT_BOOST_DATA, offset by 3"
    )

    EXCLUSIVE_ITEM_EFFECT_DATA = Symbol(
        [0x98568],
        [0x2098568],
        0x778,
        "Contains special effects for each exclusive item.\n\nEach entry is 2 bytes,"
        " with the first entry corresponding to the first exclusive item (Prism Ruff)."
        " The first byte is the exclusive item effect ID, and the second byte is an"
        " index into other data tables (related to the more generic stat boosting"
        " effects for specific monsters).",
    )

    EXCLUSIVE_ITEM_STAT_BOOST_DATA_INDEXES = Symbol(
        [0x98569], [0x2098569], 0x777, "EXCLUSIVE_ITEM_EFFECT_DATA, offset by 1"
    )

    RECOIL_MOVE_LIST = Symbol(
        [0x991B8],
        [0x20991B8],
        0x16,
        "Null-terminated list of all the recoil moves, as 2-byte move IDs.\n\ntype:"
        " struct move_id_16[11]",
    )

    PUNCH_MOVE_LIST = Symbol(
        [0x991CE],
        [0x20991CE],
        0x20,
        "Null-terminated list of all the punch moves, as 2-byte move IDs.\n\ntype:"
        " struct move_id_16[16]",
    )

    SCRIPT_VARS_LOCALS = Symbol(
        [0x9D450],
        [0x209D450],
        0x40,
        "List of special 'local' variables available to the script engine. There are 4"
        " 16-byte entries.\n\nEach entry has the same structure as an entry in"
        " SCRIPT_VARS.\n\ntype: struct script_local_var_table",
    )

    SCRIPT_VARS = Symbol(
        [0x9DDF4],
        [0x209DDF4],
        0x730,
        "List of predefined global variables that track game state, which are available"
        " to the script engine. There are 115 16-byte entries.\n\nThese variables"
        " underpin the various ExplorerScript global variables you can use in the"
        " SkyTemple SSB debugger.\n\ntype: struct script_var_table",
    )

    DUNGEON_DATA_LIST = Symbol(
        [0x9E924],
        [0x209E924],
        0x2D0,
        "Data about every dungeon in the game.\n\nThis is an array of 180 dungeon data"
        " list entry structs. Each entry is 4 bytes, and contains floor count"
        " information along with an index into the bulk of the dungeon's data in"
        " mappa_s.bin.\n\nSee the struct definitions and End45's dungeon data document"
        " for more info.\n\ntype: struct dungeon_data_list_entry[180]",
    )

    DUNGEON_RESTRICTIONS = Symbol(
        [0xA11E8],
        [0x20A11E8],
        0xC00,
        "Data related to dungeon restrictions for every dungeon in the game.\n\nThis is"
        " an array of 256 dungeon restriction structs. Each entry is 12 bytes, and"
        " contains information about restrictions within the given dungeon.\n\nSee the"
        " struct definitions and End45's dungeon data document for more info.\n\ntype:"
        " struct dungeon_restriction[256]",
    )

    SPECIAL_BAND_STAT_BOOST = Symbol(
        [0xA1DF0], [0x20A1DF0], 0x2, "Stat boost value for the Special Band."
    )

    MUNCH_BELT_STAT_BOOST = Symbol(
        [0xA1E00], [0x20A1E00], 0x2, "Stat boost value for the Munch Belt."
    )

    GUMMI_STAT_BOOST = Symbol(
        [0xA1E0C],
        [0x20A1E0C],
        0x2,
        "Stat boost value if a stat boost occurs when eating normal Gummis.",
    )

    MIN_IQ_EXCLUSIVE_MOVE_USER = Symbol([0xA1E10], [0x20A1E10], 0x4, "")

    WONDER_GUMMI_IQ_GAIN = Symbol(
        [0xA1E14], [0x20A1E14], 0x2, "IQ gain when ingesting wonder gummis."
    )

    AURA_BOW_STAT_BOOST = Symbol(
        [0xA1E1C], [0x20A1E1C], 0x2, "Stat boost value for the aura bows."
    )

    MIN_IQ_ITEM_MASTER = Symbol([0xA1E28], [0x20A1E28], 0x4, "")

    DEF_SCARF_STAT_BOOST = Symbol(
        [0xA1E2C], [0x20A1E2C], 0x2, "Stat boost value for the Defense Scarf."
    )

    POWER_BAND_STAT_BOOST = Symbol(
        [0xA1E30], [0x20A1E30], 0x2, "Stat boost value for the Power Band."
    )

    WONDER_GUMMI_STAT_BOOST = Symbol(
        [0xA1E34],
        [0x20A1E34],
        0x2,
        "Stat boost value if a stat boost occurs when eating Wonder Gummis.",
    )

    ZINC_BAND_STAT_BOOST = Symbol(
        [0xA1E38], [0x20A1E38], 0x2, "Stat boost value for the Zinc Band."
    )

    TACTICS_UNLOCK_LEVEL_TABLE = Symbol([0xA1EC4], [0x20A1EC4], 0x18, "")

    OUTLAW_LEVEL_TABLE = Symbol(
        [0xA1F1C],
        [0x20A1F1C],
        0x20,
        "Table of 2-byte outlaw levels for outlaw missions, indexed by mission rank.",
    )

    OUTLAW_MINION_LEVEL_TABLE = Symbol(
        [0xA1F3C],
        [0x20A1F3C],
        0x20,
        "Table of 2-byte outlaw minion levels for outlaw hideout missions, indexed by"
        " mission rank.",
    )

    IQ_SKILL_RESTRICTIONS = Symbol(
        [0xA1FE0],
        [0x20A1FE0],
        0x8A,
        "Table of 2-byte values for each IQ skill that represent a group. IQ skills in"
        " the same group can not be enabled at the same time.",
    )

    SECONDARY_TERRAIN_TYPES = Symbol(
        [0xA206C],
        [0x20A206C],
        0xC8,
        "The type of secondary terrain for each dungeon in the game.\n\nThis is an"
        " array of 200 bytes. Each byte is an enum corresponding to one"
        " dungeon.\n\ntype: struct secondary_terrain_type_8[200]",
    )

    SENTRY_MINIGAME_DATA = Symbol([0xA2134], [0x20A2134], None, "")

    IQ_SKILLS = Symbol(
        [0xA2200],
        [0x20A2200],
        0x114,
        "Table of 4-byte values for each IQ skill that represent the required IQ value"
        " to unlock a skill.",
    )

    IQ_GROUP_SKILLS = Symbol([0xA2314], [0x20A2314], 0x190, "")

    IQ_GUMMI_GAIN_TABLE = Symbol([0xA2834], [0x20A2834], 0x288, "")

    GUMMI_BELLY_RESTORE_TABLE = Symbol([0xA2ABC], [0x20A2ABC], 0x288, "")

    BAG_CAPACITY_TABLE = Symbol(
        [0xA2D58],
        [0x20A2D58],
        None,
        "Array of 4-byte integers containing the bag capacity for each bag level.",
    )

    SPECIAL_EPISODE_MAIN_CHARACTERS = Symbol([0xA2D78], [0x20A2D78], 0xC8, "")

    GUEST_MONSTER_DATA = Symbol(
        [0xA2E40],
        [0x20A2E40],
        0x288,
        "Data for guest monsters that join you during certain story dungeons.\n\nArray"
        " of 18 36-byte entries.\n\nSee the struct definitions and End45's dungeon data"
        " document for more info.\n\ntype: struct guest_monster[18]",
    )

    RANK_UP_TABLE = Symbol([0xA30C8], [0x20A30C8], 0xD0, "")

    MONSTER_SPRITE_DATA = Symbol([0xA332C], [0x20A332C], 0x4B0, "")

    MISSION_DUNGEON_UNLOCK_TABLE = Symbol([0xA42AC], [0x20A42AC], None, "")

    EVENTS = Symbol(
        [0xA5BD8],
        [0x20A5BD8],
        0x1584,
        "Table of levels for the script engine, in which scenes can take place. There"
        " are a version-dependent number of 12-byte entries.\n\ntype: struct"
        " script_level[length / 12]",
    )

    ENTITIES = Symbol(
        [0xA8890],
        [0x20A8890],
        0x1218,
        "Table of entities for the script engine, which can move around and do things"
        " within a scene. There are 386 12-byte entries.\n\ntype: struct"
        " script_entity[386]",
    )

    MAP_MARKER_PLACEMENTS = Symbol(
        [0xA9D70],
        [0x20A9D70],
        0x9B0,
        "The map marker position of each dungeon on the Wonder Map.\n\nThis is an array"
        " of 310 map marker structs. Each entry is 8 bytes, and contains positional"
        " information about a dungeon on the map.\n\nSee the struct definitions and"
        " End45's dungeon data document for more info.\n\ntype: struct map_marker[310]",
    )

    MEMORY_ALLOCATION_ARENA_GETTERS = Symbol(
        [0xAF7A0],
        [0x20AF7A0],
        0x8,
        "Functions to get the desired memory arena for allocating and freeing heap"
        " memory.\n\ntype: struct mem_arena_getters",
    )

    PRNG_SEQUENCE_NUM = Symbol(
        [0xAF7CC],
        [0x20AF7CC],
        0x2,
        "[Runtime] The current PRNG sequence number for the general-purpose PRNG. See"
        " Rand16Bit for more information on how the general-purpose PRNG works.",
    )

    LOADED_OVERLAY_GROUP_0 = Symbol(
        [0xAFAD0],
        [0x20AFAD0],
        0x4,
        "[Runtime] The overlay group ID of the overlay currently loaded in slot 0. A"
        " group ID of 0 denotes no overlay.\n\nOverlay group IDs that can be loaded in"
        " slot 0:\n- 0x06 (overlay 3)\n- 0x07 (overlay 6)\n- 0x08 (overlay 4)\n- 0x09"
        " (overlay 5)\n- 0x0A (overlay 7)\n- 0x0B (overlay 8)\n- 0x0C (overlay 9)\n-"
        " 0x10 (overlay 12)\n- 0x11 (overlay 13)\n- 0x12 (overlay 14)\n- 0x13 (overlay"
        " 15)\n- 0x14 (overlay 16)\n- 0x15 (overlay 17)\n- 0x16 (overlay 18)\n- 0x17"
        " (overlay 19)\n- 0x18 (overlay 20)\n- 0x19 (overlay 21)\n- 0x1A (overlay"
        " 22)\n- 0x1B (overlay 23)\n- 0x1C (overlay 24)\n- 0x1D (overlay 25)\n- 0x1E"
        " (overlay 26)\n- 0x1F (overlay 27)\n- 0x20 (overlay 28)\n- 0x21 (overlay"
        " 30)\n- 0x22 (overlay 31)\n- 0x23 (overlay 32)\n- 0x24 (overlay 33)\n\ntype:"
        " enum overlay_group_id",
    )

    LOADED_OVERLAY_GROUP_1 = Symbol(
        [0xAFAD4],
        [0x20AFAD4],
        0x4,
        "[Runtime] The overlay group ID of the overlay currently loaded in slot 1. A"
        " group ID of 0 denotes no overlay.\n\nOverlay group IDs that can be loaded in"
        " slot 1:\n- 0x4 (overlay 1)\n- 0x5 (overlay 2)\n- 0xD (overlay 11)\n- 0xE"
        " (overlay 29)\n- 0xF (overlay 34)\n\ntype: enum overlay_group_id",
    )

    LOADED_OVERLAY_GROUP_2 = Symbol(
        [0xAFAD8],
        [0x20AFAD8],
        0x4,
        "[Runtime] The overlay group ID of the overlay currently loaded in slot 2. A"
        " group ID of 0 denotes no overlay.\n\nOverlay group IDs that can be loaded in"
        " slot 2:\n- 0x1 (overlay 0)\n- 0x2 (overlay 10)\n- 0x3 (overlay 35)\n\ntype:"
        " enum overlay_group_id",
    )

    PACK_FILE_OPENED = Symbol(
        [0xAFF54],
        [0x20AFF54],
        0x4,
        "[Runtime] A pointer to the 6 opened Pack files (listed at"
        " PACK_FILE_PATHS_TABLE)\n\ntype: struct pack_file_opened*",
    )

    PACK_FILE_PATHS_TABLE = Symbol(
        [0xAFF58],
        [0x20AFF58],
        0x18,
        "List of pointers to path strings to all known pack files.\nThe game uses this"
        " table to load its resources when launching dungeon mode.\n\ntype: char*[6]",
    )

    GAME_STATE_VALUES = Symbol([0xAFF70], [0x20AFF70], None, "[Runtime]")

    DUNGEON_MOVE_TABLES = Symbol(
        [0xAFFA8],
        [0x20AFFA8],
        None,
        "[Runtime] Seems to be some sort of region (a table of tables?) that holds"
        " pointers to various important tables related to moves.",
    )

    MOVE_DATA_TABLE_PTR = Symbol(
        [0xAFFB0],
        [0x20AFFB0],
        0x4,
        "[Runtime] Points to the contents of the move data table loaded from"
        " waza_p.bin\n\ntype: struct move_data_table*",
    )

    LANGUAGE_INFO_DATA = Symbol([0xB05A8], [0x20B05A8], None, "[Runtime]")

    NOTIFY_NOTE = Symbol(
        [0xB0814],
        [0x20B0814],
        None,
        "[Runtime] Flag related to saving and loading state?\n\ntype: bool",
    )

    DEFAULT_HERO_ID = Symbol(
        [0xB0818],
        [0x20B0818],
        0x2,
        "The default monster ID for the hero (0x4: Charmander)\n\ntype: struct"
        " monster_id_16",
    )

    DEFAULT_PARTNER_ID = Symbol(
        [0xB081A],
        [0x20B081A],
        0x2,
        "The default monster ID for the partner (0x1: Bulbasaur)\n\ntype: struct"
        " monster_id_16",
    )

    GAME_MODE = Symbol([0xB088C], [0x20B088C], None, "[Runtime]\n\ntype: uint8_t")

    ADVENTURE_LOG_PTR = Symbol(
        [0xB0894], [0x20B0894], 0x4, "[Runtime]\n\ntype: struct adventure_log*"
    )

    ITEM_TABLES_PTRS_1 = Symbol([0xB1264], [0x20B1264], 0x68, "")

    SMD_EVENTS_FUN_TABLE = Symbol([0xB14D4], [0x20B14D4], 0x1FC, "")


class EuArm9Section:
    name = "arm9"
    description = (
        "Hard-coded immediate values (literals) in instructions within the ARM 9"
        " binary."
    )
    loadaddress = 0x2000000
    length = 0xB7D38
    functions = EuArm9Functions
    data = EuArm9Data


class EuOverlay0Functions:
    pass


class EuOverlay0Data:
    TOP_MENU_MUSIC_ID = Symbol(
        [0x15F4], [0x22BE9B4], None, "Music ID to play in the top menu."
    )


class EuOverlay0Section:
    name = "overlay0"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 0."
    )
    loadaddress = 0x22BD3C0
    length = 0x60880
    functions = EuOverlay0Functions
    data = EuOverlay0Data


class EuOverlay10Functions:
    SprintfStatic = Symbol(
        [0x9CC, 0x4DD4],
        [0x22BDD8C, 0x22C2194],
        None,
        "Statically defined copy of sprintf(3) in overlay 10. See arm9.yml for more"
        " information.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )


class EuOverlay10Data:
    FIRST_DUNGEON_WITH_MONSTER_HOUSE_TRAPS = Symbol(
        [0x79A4],
        [0x22C4D64],
        0x1,
        "The first dungeon that can have extra traps spawn in Monster Houses, Dark"
        " Hill\n\ntype: struct dungeon_id_8",
    )

    BAD_POISON_DAMAGE_COOLDOWN = Symbol(
        [0x79AC],
        [0x22C4D6C],
        0x2,
        "The number of turns between passive bad poison (toxic) damage.",
    )

    PROTEIN_STAT_BOOST = Symbol(
        [0x79B8],
        [0x22C4D78],
        0x2,
        "The permanent attack boost from ingesting a Protein.",
    )

    SPAWN_CAP_NO_MONSTER_HOUSE = Symbol(
        [0x79C8],
        [0x22C4D88],
        None,
        "The maximum number of enemies that can spawn on a floor without a monster"
        " house (15).",
    )

    OREN_BERRY_DAMAGE = Symbol(
        [0x79D0], [0x22C4D90], 0x2, "Damage dealt by eating an Oren Berry."
    )

    SITRUS_BERRY_HP_RESTORATION = Symbol(
        [0x7A10],
        [0x22C4DD0],
        0x2,
        "The amount of HP restored by eating a Sitrus Berry.",
    )

    EXP_ELITE_EXP_BOOST = Symbol(
        [0x7A40],
        [0x22C4E00],
        0x2,
        "The percentage increase in experience from the Exp. Elite IQ skill",
    )

    MONSTER_HOUSE_MAX_NON_MONSTER_SPAWNS = Symbol(
        [0x7A44],
        [0x22C4E04],
        0x2,
        "The maximum number of extra non-monster spawns (items/traps) in a Monster"
        " House, 7",
    )

    GOLD_THORN_POWER = Symbol(
        [0x7A68], [0x22C4E28], 0x2, "Attack power for Golden Thorns."
    )

    SPAWN_COOLDOWN = Symbol(
        [0x7A74],
        [0x22C4E34],
        0x2,
        "The number of turns between enemy spawns under normal conditions.",
    )

    ORAN_BERRY_FULL_HP_BOOST = Symbol(
        [0x7A8C],
        [0x22C4E4C],
        0x2,
        "The permanent HP boost from eating an Oran Berry at full HP (0).",
    )

    LIFE_SEED_HP_BOOST = Symbol(
        [0x7A90], [0x22C4E50], 0x2, "The permanent HP boost from eating a Life Seed."
    )

    EXCLUSIVE_ITEM_EXP_BOOST = Symbol(
        [0x7B24],
        [0x22C4EE4],
        0x2,
        "The percentage increase in experience from exp-boosting exclusive items",
    )

    INTIMIDATOR_ACTIVATION_CHANCE = Symbol(
        [0x7B50],
        [0x22C4F10],
        0x2,
        "The percentage chance that Intimidator will activate.",
    )

    ORAN_BERRY_HP_RESTORATION = Symbol(
        [0x7B84], [0x22C4F44], 0x2, "The amount of HP restored by eating a Oran Berry."
    )

    SITRUS_BERRY_FULL_HP_BOOST = Symbol(
        [0x7B8C],
        [0x22C4F4C],
        0x2,
        "The permanent HP boost from eating a Sitrus Berry at full HP.",
    )

    BURN_DAMAGE_COOLDOWN = Symbol(
        [0x7BA8], [0x22C4F68], 0x2, "The number of turns between passive burn damage."
    )

    STICK_POWER = Symbol([0x7BBC], [0x22C4F7C], 0x2, "Attack power for Sticks.")

    SPAWN_COOLDOWN_THIEF_ALERT = Symbol(
        [0x7BD8],
        [0x22C4F98],
        0x2,
        "The number of turns between enemy spawns when the Thief Alert condition is"
        " active.",
    )

    MONSTER_HOUSE_MAX_MONSTER_SPAWNS = Symbol(
        [0x7BF8],
        [0x22C4FB8],
        0x2,
        "The maximum number of monster spawns in a Monster House, 30, but multiplied by"
        " 2/3 for some reason (so the actual maximum is 45)",
    )

    SPEED_BOOST_TURNS = Symbol(
        [0x7C04],
        [0x22C4FC4],
        None,
        "Number of turns (250) after which Speed Boost will trigger and increase speed"
        " by one stage.",
    )

    MIRACLE_CHEST_EXP_BOOST = Symbol(
        [0x7C30],
        [0x22C4FF0],
        0x2,
        "The percentage increase in experience from the Miracle Chest item",
    )

    WONDER_CHEST_EXP_BOOST = Symbol(
        [0x7C34],
        [0x22C4FF4],
        0x2,
        "The percentage increase in experience from the Wonder Chest item",
    )

    SPAWN_CAP_WITH_MONSTER_HOUSE = Symbol(
        [0x7C3C],
        [0x22C4FFC],
        None,
        "The maximum number of enemies that can spawn on a floor with a monster house,"
        " not counting those in the monster house (4).",
    )

    POISON_DAMAGE_COOLDOWN = Symbol(
        [0x7C40], [0x22C5000], 0x2, "The number of turns between passive poison damage."
    )

    GEO_PEBBLE_DAMAGE = Symbol(
        [0x7C4C], [0x22C500C], 0x2, "Damage dealt by Geo Pebbles."
    )

    GRAVELEROCK_DAMAGE = Symbol(
        [0x7C50], [0x22C5010], 0x2, "Damage dealt by Gravelerocks."
    )

    RARE_FOSSIL_DAMAGE = Symbol(
        [0x7C54], [0x22C5014], 0x2, "Damage dealt by Rare Fossils."
    )

    GINSENG_CHANCE_3 = Symbol(
        [0x7C58],
        [0x22C5018],
        0x2,
        "The percentage chance for...something to be set to 3 in a calculation related"
        " to the Ginseng boost.",
    )

    ZINC_STAT_BOOST = Symbol(
        [0x7C5C],
        [0x22C501C],
        0x2,
        "The permanent special defense boost from ingesting a Zinc.",
    )

    IRON_STAT_BOOST = Symbol(
        [0x7C60],
        [0x22C5020],
        0x2,
        "The permanent defense boost from ingesting an Iron.",
    )

    CALCIUM_STAT_BOOST = Symbol(
        [0x7C64],
        [0x22C5024],
        0x2,
        "The permanent special attack boost from ingesting a Calcium.",
    )

    CORSOLA_TWIG_POWER = Symbol(
        [0x7C70], [0x22C5030], 0x2, "Attack power for Corsola Twigs."
    )

    CACNEA_SPIKE_POWER = Symbol(
        [0x7C74], [0x22C5034], 0x2, "Attack power for Cacnea Spikes."
    )

    GOLD_FANG_POWER = Symbol([0x7C78], [0x22C5038], 0x2, "Attack power for Gold Fangs.")

    SILVER_SPIKE_POWER = Symbol(
        [0x7C7C], [0x22C503C], 0x2, "Attack power for Silver Spikes."
    )

    IRON_THORN_POWER = Symbol(
        [0x7C80], [0x22C5040], 0x2, "Attack power for Iron Thorns."
    )

    SLEEP_DURATION_RANGE = Symbol(
        [0x7CB8],
        [0x22C5078],
        0x4,
        "Appears to control the range of turns for which the sleep condition can"
        " last.\n\nThe first two bytes are the low value of the range, and the later"
        " two bytes are the high value.",
    )

    POWER_PITCHER_DAMAGE_MULTIPLIER = Symbol(
        [0x7D90],
        [0x22C5150],
        0x4,
        "The multiplier for projectile damage from Power Pitcher (1.5), as a binary"
        " fixed-point number (8 fraction bits)",
    )

    AIR_BLADE_DAMAGE_MULTIPLIER = Symbol(
        [0x7DDC],
        [0x22C519C],
        None,
        "The multiplier for damage from the Air Blade (1.5), as a binary fixed-point"
        " number (8 fraction bits)",
    )

    SPEED_BOOST_DURATION_RANGE = Symbol(
        [0x7E20],
        [0x22C51E0],
        0x4,
        "Appears to control the range of turns for which a speed boost can last.\n\nThe"
        " first two bytes are the low value of the range, and the later two bytes are"
        " the high value.",
    )

    OFFENSIVE_STAT_STAGE_MULTIPLIERS = Symbol(
        [0x8330],
        [0x22C56F0],
        0x54,
        "Table of multipliers for offensive stats (attack/special attack) for each"
        " stage 0-20, as binary fixed-point numbers (8 fraction bits)",
    )

    DEFENSIVE_STAT_STAGE_MULTIPLIERS = Symbol(
        [0x8384],
        [0x22C5744],
        0x54,
        "Table of multipliers for defensive stats (defense/special defense) for each"
        " stage 0-20, as binary fixed-point numbers (8 fraction bits)",
    )

    RANDOM_MUSIC_ID_TABLE = Symbol(
        [0x8794],
        [0x22C5B54],
        0xF0,
        "Table of music IDs for dungeons with a random assortment of music"
        " tracks.\n\nThis is a table with 30 rows, each with 4 2-byte music IDs. Each"
        " row contains the possible music IDs for a given group, from which the music"
        " track will be selected randomly.\n\ntype: struct music_id_16[30][4]",
    )

    MALE_ACCURACY_STAGE_MULTIPLIERS = Symbol(
        [0x89A4],
        [0x22C5D64],
        0x54,
        "Table of multipliers for the accuracy stat for males for each stage 0-20, as"
        " binary fixed-point numbers (8 fraction bits)",
    )

    MALE_EVASION_STAGE_MULTIPLIERS = Symbol(
        [0x89F8],
        [0x22C5DB8],
        0x54,
        "Table of multipliers for the evasion stat for males for each stage 0-20, as"
        " binary fixed-point numbers (8 fraction bits)",
    )

    FEMALE_ACCURACY_STAGE_MULTIPLIERS = Symbol(
        [0x8A4C],
        [0x22C5E0C],
        0x54,
        "Table of multipliers for the accuracy stat for females for each stage 0-20, as"
        " binary fixed-point numbers (8 fraction bits)",
    )

    FEMALE_EVASION_STAGE_MULTIPLIERS = Symbol(
        [0x8AA0],
        [0x22C5E60],
        0x54,
        "Table of multipliers for the evasion stat for females for each stage 0-20, as"
        " binary fixed-point numbers (8 fraction bits)",
    )

    MUSIC_ID_TABLE = Symbol(
        [0x8AF4],
        [0x22C5EB4],
        0x154,
        "List of music IDs used in dungeons with a single music track.\n\nThis is an"
        " array of 170 2-byte music IDs, and is indexed into by the music value in the"
        " floor properties struct for a given floor. Music IDs with the highest bit set"
        " (0x8000) are indexes into the RANDOM_MUSIC_ID_TABLE.\n\ntype: struct"
        " music_id_16[170] (or not a music ID if the highest bit is set)",
    )

    TYPE_MATCHUP_TABLE = Symbol(
        [0x8C48],
        [0x22C6008],
        0x288,
        "Table of type matchups.\n\nEach row corresponds to the type matchups of a"
        " specific attack type, with each entry within the row specifying the type's"
        " effectiveness against a target type.\n\ntype: struct type_matchup_table",
    )

    FIXED_ROOM_MONSTER_SPAWN_STATS_TABLE = Symbol(
        [0x8ED0],
        [0x22C6290],
        0x4A4,
        "Table of stats for monsters that can spawn in fixed rooms, pointed into by the"
        " FIXED_ROOM_MONSTER_SPAWN_TABLE.\n\nThis is an array of 99 12-byte entries"
        " containing stat spreads for one monster entry each.\n\ntype: struct"
        " fixed_room_monster_spawn_stats_entry[99]",
    )

    TILESET_PROPERTIES = Symbol([0x98B4], [0x22C6C74], 0x954, "")

    FIXED_ROOM_PROPERTIES_TABLE = Symbol(
        [0xA208],
        [0x22C75C8],
        0xC00,
        "Table of properties for fixed rooms.\n\nThis is an array of 256 12-byte"
        " entries containing properties for a given fixed room ID.\n\nSee the struct"
        " definitions and End45's dungeon data document for more info.\n\ntype: struct"
        " fixed_room_properties_entry[256]",
    )

    MOVE_ANIMATION_INFO = Symbol([0xC5FC], [0x22C99BC], None, "")


class EuOverlay10Section:
    name = "overlay10"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 10."
    )
    loadaddress = 0x22BD3C0
    length = 0x1F7A0
    functions = EuOverlay10Functions
    data = EuOverlay10Data


class EuOverlay34Functions:
    pass


class EuOverlay34Data:
    UNKNOWN_MENU_CONFIRM = Symbol([0xD4C], [0x22DD8CC], 0x18, "")

    DUNGEON_DEBUG_MENU = Symbol([0xD74], [0x22DD8F4], 0x28, "")


class EuOverlay34Section:
    name = "overlay34"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 34."
    )
    loadaddress = 0x22DCB80
    length = 0xDC0
    functions = EuOverlay34Functions
    data = EuOverlay34Data


class EuOverlay1Functions:
    pass


class EuOverlay1Data:
    CONTINUE_CHOICE = Symbol([0x11F74], [0x233BCB4], 0x20, "")

    SUBMENU = Symbol([0x11F94], [0x233BCD4], 0x48, "")

    MAIN_MENU = Symbol([0x11FDC], [0x233BD1C], 0xA0, "")

    MAIN_MENU_CONFIRM = Symbol([0x12158], [0x233BE98], 0x18, "")

    MAIN_DEBUG_MENU_1 = Symbol([0x1221C], [0x233BF5C], 0x60, "")

    MAIN_DEBUG_MENU_2 = Symbol([0x1229C], [0x233BFDC], 0x38, "")


class EuOverlay1Section:
    name = "overlay1"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 1."
    )
    loadaddress = 0x2329D40
    length = 0x12C80
    functions = EuOverlay1Functions
    data = EuOverlay1Data


class EuOverlay4Functions:
    pass


class EuOverlay4Data:
    pass


class EuOverlay4Section:
    name = "overlay4"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 4."
    )
    loadaddress = 0x233D200
    length = 0x2BE0
    functions = EuOverlay4Functions
    data = EuOverlay4Data


class EuOverlay6Functions:
    pass


class EuOverlay6Data:
    pass


class EuOverlay6Section:
    name = "overlay6"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 6."
    )
    loadaddress = 0x233D200
    length = 0x2460
    functions = EuOverlay6Functions
    data = EuOverlay6Data


class EuOverlay7Functions:
    pass


class EuOverlay7Data:
    pass


class EuOverlay7Section:
    name = "overlay7"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 7."
    )
    loadaddress = 0x233D200
    length = 0x3300
    functions = EuOverlay7Functions
    data = EuOverlay7Data


class EuOverlay9Functions:
    pass


class EuOverlay9Data:
    TOP_MENU_RETURN_MUSIC_ID = Symbol(
        [0xE80],
        [0x233E080],
        None,
        "Song playing in the main menu when returning from the Sky Jukebox.",
    )


class EuOverlay9Section:
    name = "overlay9"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 9."
    )
    loadaddress = 0x233D200
    length = 0x2D80
    functions = EuOverlay9Functions
    data = EuOverlay9Data


class EuOverlay30Functions:
    pass


class EuOverlay30Data:
    pass


class EuOverlay30Section:
    name = "overlay30"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 30."
    )
    loadaddress = 0x2383420
    length = 0x38A0
    functions = EuOverlay30Functions
    data = EuOverlay30Data


class EuOverlay31Functions:
    pass


class EuOverlay31Data:
    DUNGEON_MAIN_MENU = Symbol([0x75D8], [0x238A9F8], 0x40, "")

    DUNGEON_SUBMENU_1 = Symbol([0x7674], [0x238AA94], 0x20, "")

    DUNGEON_SUBMENU_2 = Symbol([0x7694], [0x238AAB4], 0x20, "")

    DUNGEON_SUBMENU_3 = Symbol([0x76B4], [0x238AAD4], 0x20, "")

    DUNGEON_SUBMENU_4 = Symbol([0x76D4], [0x238AAF4], 0x20, "")

    DUNGEON_SUBMENU_5 = Symbol([0x7920], [0x238AD40], 0x18, "")

    DUNGEON_SUBMENU_6 = Symbol([0x79A4], [0x238ADC4], 0x48, "")


class EuOverlay31Section:
    name = "overlay31"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 31."
    )
    loadaddress = 0x2383420
    length = 0x7AA0
    functions = EuOverlay31Functions
    data = EuOverlay31Data


class EuOverlay13Functions:
    pass


class EuOverlay13Data:
    STARTERS_PARTNER_IDS = Symbol(
        [0x1F4C], [0x238CBCC], 0x2A, "type: struct monster_id_16[21]"
    )

    STARTERS_HERO_IDS = Symbol(
        [0x1F78], [0x238CBF8], 0x40, "type: struct monster_id_16[32]"
    )

    STARTERS_STRINGS = Symbol([0x200C], [0x238CC8C], 0x60, "")

    QUIZ_QUESTION_STRINGS = Symbol([0x206C], [0x238CCEC], 0x84, "")

    QUIZ_ANSWER_STRINGS = Symbol([0x20F0], [0x238CD70], 0x160, "")

    UNKNOWN_MENU_1 = Symbol([0x2D8C], [0x238DA0C], 0x48, "")


class EuOverlay13Section:
    name = "overlay13"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 13."
    )
    loadaddress = 0x238AC80
    length = 0x2E80
    functions = EuOverlay13Functions
    data = EuOverlay13Data


class EuOverlay14Functions:
    pass


class EuOverlay14Data:
    FOOTPRINT_DEBUG_MENU = Symbol([0x39C0], [0x238E640], 0x48, "")


class EuOverlay14Section:
    name = "overlay14"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 14."
    )
    loadaddress = 0x238AC80
    length = 0x3B40
    functions = EuOverlay14Functions
    data = EuOverlay14Data


class EuOverlay15Functions:
    pass


class EuOverlay15Data:
    BANK_MAIN_MENU = Symbol([0xF40], [0x238BBC0], 0x28, "")


class EuOverlay15Section:
    name = "overlay15"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 15."
    )
    loadaddress = 0x238AC80
    length = 0x1080
    functions = EuOverlay15Functions
    data = EuOverlay15Data


class EuOverlay16Functions:
    pass


class EuOverlay16Data:
    EVO_MENU_CONFIRM = Symbol([0x2BCC], [0x238D84C], 0x18, "")

    EVO_SUBMENU = Symbol([0x2BE4], [0x238D864], 0x20, "")

    EVO_MAIN_MENU = Symbol([0x2C04], [0x238D884], 0x20, "")


class EuOverlay16Section:
    name = "overlay16"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 16."
    )
    loadaddress = 0x238AC80
    length = 0x2D20
    functions = EuOverlay16Functions
    data = EuOverlay16Data


class EuOverlay18Functions:
    pass


class EuOverlay18Data:
    MOVES_MENU_CONFIRM = Symbol([0x31E0], [0x238DE60], 0x18, "")

    MOVES_SUBMENU_1 = Symbol([0x31F8], [0x238DE78], 0x20, "")

    MOVES_SUBMENU_2 = Symbol([0x3218], [0x238DE98], 0x20, "")

    MOVES_MAIN_MENU = Symbol([0x3238], [0x238DEB8], 0x20, "")

    MOVES_SUBMENU_3 = Symbol([0x3258], [0x238DED8], 0x28, "")

    MOVES_SUBMENU_4 = Symbol([0x3280], [0x238DF00], 0x30, "")

    MOVES_SUBMENU_5 = Symbol([0x32B0], [0x238DF30], 0x48, "")

    MOVES_SUBMENU_6 = Symbol([0x32F8], [0x238DF78], 0x48, "")

    MOVES_SUBMENU_7 = Symbol([0x3340], [0x238DFC0], 0x48, "")


class EuOverlay18Section:
    name = "overlay18"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 18."
    )
    loadaddress = 0x238AC80
    length = 0x3500
    functions = EuOverlay18Functions
    data = EuOverlay18Data


class EuOverlay21Functions:
    pass


class EuOverlay21Data:
    SWAP_SHOP_MENU_CONFIRM = Symbol([0x28F8], [0x238D578], 0x18, "")

    SWAP_SHOP_SUBMENU_1 = Symbol([0x2910], [0x238D590], 0x18, "")

    SWAP_SHOP_SUBMENU_2 = Symbol([0x2928], [0x238D5A8], 0x20, "")

    SWAP_SHOP_MAIN_MENU_1 = Symbol([0x2948], [0x238D5C8], 0x20, "")

    SWAP_SHOP_MAIN_MENU_2 = Symbol([0x2968], [0x238D5E8], 0x28, "")

    SWAP_SHOP_SUBMENU_3 = Symbol([0x2990], [0x238D610], 0x30, "")


class EuOverlay21Section:
    name = "overlay21"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 21."
    )
    loadaddress = 0x238AC80
    length = 0x2E20
    functions = EuOverlay21Functions
    data = EuOverlay21Data


class EuOverlay22Functions:
    pass


class EuOverlay22Data:
    SHOP_MENU_CONFIRM = Symbol([0x4728], [0x238F3A8], 0x18, "")

    SHOP_MAIN_MENU_1 = Symbol([0x4740], [0x238F3C0], 0x20, "")

    SHOP_MAIN_MENU_2 = Symbol([0x4760], [0x238F3E0], 0x20, "")

    SHOP_MAIN_MENU_3 = Symbol([0x4780], [0x238F400], 0x30, "")


class EuOverlay22Section:
    name = "overlay22"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 22."
    )
    loadaddress = 0x238AC80
    length = 0x4B40
    functions = EuOverlay22Functions
    data = EuOverlay22Data


class EuOverlay23Functions:
    pass


class EuOverlay23Data:
    STORAGE_MENU_CONFIRM = Symbol([0x31BC], [0x238DE3C], 0x18, "")

    STORAGE_MAIN_MENU_1 = Symbol([0x31D4], [0x238DE54], 0x20, "")

    STORAGE_MAIN_MENU_2 = Symbol([0x31F4], [0x238DE74], 0x20, "")

    STORAGE_MAIN_MENU_3 = Symbol([0x3214], [0x238DE94], 0x20, "")

    STORAGE_MAIN_MENU_4 = Symbol([0x3234], [0x238DEB4], 0x28, "")


class EuOverlay23Section:
    name = "overlay23"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 23."
    )
    loadaddress = 0x238AC80
    length = 0x3780
    functions = EuOverlay23Functions
    data = EuOverlay23Data


class EuOverlay24Functions:
    pass


class EuOverlay24Data:
    DAYCARE_MENU_CONFIRM = Symbol([0x23E0], [0x238D060], 0x18, "")

    DAYCARE_MAIN_MENU = Symbol([0x23F8], [0x238D078], 0x20, "")


class EuOverlay24Section:
    name = "overlay24"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 24."
    )
    loadaddress = 0x238AC80
    length = 0x24E0
    functions = EuOverlay24Functions
    data = EuOverlay24Data


class EuOverlay26Functions:
    pass


class EuOverlay26Data:
    pass


class EuOverlay26Section:
    name = "overlay26"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 26."
    )
    loadaddress = 0x238AC80
    length = 0xE40
    functions = EuOverlay26Functions
    data = EuOverlay26Data


class EuOverlay27Functions:
    pass


class EuOverlay27Data:
    DISCARD_ITEMS_MENU_CONFIRM = Symbol([0x281C], [0x238D49C], 0x18, "")

    DISCARD_ITEMS_SUBMENU_1 = Symbol([0x2834], [0x238D4B4], 0x20, "")

    DISCARD_ITEMS_SUBMENU_2 = Symbol([0x2854], [0x238D4D4], 0x20, "")

    DISCARD_ITEMS_MAIN_MENU = Symbol([0x2874], [0x238D4F4], 0x28, "")


class EuOverlay27Section:
    name = "overlay27"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 27."
    )
    loadaddress = 0x238AC80
    length = 0x2D60
    functions = EuOverlay27Functions
    data = EuOverlay27Data


class EuOverlay32Functions:
    pass


class EuOverlay32Data:
    pass


class EuOverlay32Section:
    name = "overlay32"
    description = "Unused; all zeroes."
    loadaddress = 0x2383420
    length = 0x20
    functions = EuOverlay32Functions
    data = EuOverlay32Data


class EuRamFunctions:
    pass


class EuRamData:
    DUNGEON_COLORMAP_PTR = Symbol(
        [0x1BA634],
        [0x21BA634],
        0x4,
        "Pointer to a colormap used to render colors in a dungeon.\n\nThe colormap is a"
        " list of 4-byte RGB colors of the form {R, G, B, padding}, which the game"
        " indexes into when rendering colors. Some weather conditions modify the"
        " colormap, which is how the color scheme changes when it's, e.g., raining.",
    )

    DUNGEON_STRUCT = Symbol(
        [0x1BA674],
        [0x21BA674],
        0x2CB14,
        "The dungeon context struct used for tons of stuff in dungeon mode. See struct"
        " dungeon in the C headers.\n\nThis struct never seems to be referenced"
        " directly, and is instead usually accessed via DUNGEON_PTR in overlay"
        " 29.\n\ntype: struct dungeon",
    )

    MOVE_DATA_TABLE = Symbol(
        [0x211D0C],
        [0x2211D0C],
        0x38C6,
        "The move data table loaded directly from /BALANCE/waza_p.bin. See struct"
        " move_data_table in the C headers.\n\nPointed to by MOVE_DATA_TABLE_PTR in the"
        " ARM 9 binary.\n\ntype: struct move_data_table",
    )

    FRAMES_SINCE_LAUNCH = Symbol(
        [0x2A3E8C, 0x2A3EDC],
        [0x22A3E8C, 0x22A3EDC],
        0x4,
        "Starts at 0 when the game is first launched, and continuously ticks up once"
        " per frame while the game is running.",
    )

    BAG_ITEMS = Symbol(
        [0x2A4164],
        [0x22A4164],
        0x12C,
        "Array of item structs within the player's bag.\n\nWhile the game only allows a"
        " maximum of 48 items during normal play, it seems to read up to 50 item slots"
        " if filled.\n\ntype: struct item[50]",
    )

    BAG_ITEMS_PTR = Symbol([0x2A44E8], [0x22A44E8], 0x4, "Pointer to BAG_ITEMS.")

    STORAGE_ITEMS = Symbol(
        [0x2A44EE],
        [0x22A44EE],
        0x7D0,
        "Array of item IDs in the player's item storage.\n\nFor stackable items, the"
        " quantities are stored elsewhere, in STORAGE_ITEM_QUANTITIES.\n\ntype: struct"
        " item_id_16[1000]",
    )

    STORAGE_ITEM_QUANTITIES = Symbol(
        [0x2A4CBE],
        [0x22A4CBE],
        0x7D0,
        "Array of 1000 2-byte (unsigned) quantities corresponding to the item IDs in"
        " STORAGE_ITEMS.\n\nIf the corresponding item ID is not a stackable item, the"
        " entry in this array is unused, and will be 0.",
    )

    KECLEON_SHOP_ITEMS_PTR = Symbol(
        [0x2A5490], [0x22A5490], 0x4, "Pointer to KECLEON_SHOP_ITEMS."
    )

    KECLEON_SHOP_ITEMS = Symbol(
        [0x2A5494],
        [0x22A5494],
        0x20,
        "Array of up to 8 items in the Kecleon Shop of the form {struct item_id_16 id,"
        " uint16_t quantity}.\n\nIf there are fewer than 8 items, the array is expected"
        " to be null-terminated.",
    )

    UNUSED_KECLEON_SHOP_ITEMS = Symbol(
        [0x2A54B4],
        [0x22A54B4],
        0x20,
        "Seems to be another array like KECLEON_SHOP_ITEMS, but don't actually appear"
        " to be used by the Kecleon Shop.",
    )

    KECLEON_WARES_ITEMS_PTR = Symbol(
        [0x2A54D4], [0x22A54D4], 0x4, "Pointer to KECLEON_WARES_ITEMS."
    )

    KECLEON_WARES_ITEMS = Symbol(
        [0x2A54D8],
        [0x22A54D8],
        0x10,
        "Array of up to 4 items in Kecleon Wares of the form {struct item_id_16 id,"
        " uint16_t quantity}.\n\nIf there are fewer than 4 items, the array is expected"
        " to be null-terminated.",
    )

    UNUSED_KECLEON_WARES_ITEMS = Symbol(
        [0x2A54E8],
        [0x22A54E8],
        0x10,
        "Seems to be another array like KECLEON_WARES_ITEMS, but don't actually appear"
        " to be used by Kecleon Wares.",
    )

    MONEY_CARRIED = Symbol(
        [0x2A54F8],
        [0x22A54F8],
        0x4,
        "The amount of money the player is currently carrying.",
    )

    MONEY_STORED = Symbol(
        [0x2A5504],
        [0x22A5504],
        0x4,
        "The amount of money the player currently has stored in the Duskull Bank.",
    )

    LAST_NEW_MOVE = Symbol(
        [0x2AB78C],
        [0x22AB78C],
        0x8,
        "Move struct of the last new move introduced when learning a new move. Persists"
        " even after the move selection is made in the menu.\n\ntype: struct move",
    )

    SCRIPT_VARS_VALUES = Symbol(
        [0x2AB9EC],
        [0x22AB9EC],
        0x400,
        "The table of game variable values. Its structure is determined by"
        " SCRIPT_VARS.\n\nNote that with the script variable list defined in"
        " SCRIPT_VARS, the used length of this table is actually only 0x2B4. However,"
        " the real length of this table is 0x400 based on the game code.\n\ntype:"
        " struct script_var_value_table",
    )

    BAG_LEVEL = Symbol(
        [0x2ABA9C],
        [0x22ABA9C],
        0x1,
        "The player's bag level, which determines the bag capacity. This indexes"
        " directly into the BAG_CAPACITY_TABLE in the ARM9 binary.",
    )

    DEBUG_SPECIAL_EPISODE_NUMBER = Symbol(
        [0x2ABDEC],
        [0x22ABDEC],
        0x1,
        "The number of the special episode currently being played.\n\n0: normal,"
        " Bidoof's Wish\n1: Igglybuff the Prodigy\n2: Today's 'Oh My Gosh'\n3: Here"
        " Comes Team Charm!\n4: In the Future of Darkness",
    )

    PENDING_DUNGEON_ID = Symbol(
        [0x2ABE3C],
        [0x22ABE3C],
        0x1,
        "The ID of the selected dungeon when setting off from the"
        " overworld.\n\nControls the text and map location during the 'map cutscene'"
        " just before entering a dungeon, as well as the actual dungeon loaded"
        " afterwards.\n\ntype: struct dungeon_id_8",
    )

    PENDING_STARTING_FLOOR = Symbol(
        [0x2ABE3D],
        [0x22ABE3D],
        0x1,
        "The floor number to start from in the dungeon specified by"
        " PENDING_DUNGEON_ID.",
    )

    PLAY_TIME_SECONDS = Symbol(
        [0x2ABFD4], [0x22ABFD4], 0x4, "The player's total play time in seconds."
    )

    PLAY_TIME_FRAME_COUNTER = Symbol(
        [0x2ABFD8],
        [0x22ABFD8],
        0x1,
        "Counts from 0-59 in a loop, with the play time being incremented by 1 second"
        " with each rollover.",
    )

    TEAM_NAME = Symbol(
        [0x2AC258],
        [0x22AC258],
        0xC,
        "The team name.\n\nA null-terminated string, with a maximum length of 10."
        " Presumably encoded with the ANSI/Shift JIS encoding the game typically"
        " uses.\n\nThis is presumably part of a larger struct, together with other"
        " nearby data.",
    )

    HERO_SPECIES_ID = Symbol(
        [0x2AC724],
        [0x22AC724],
        0x2,
        "The hero's species ID.\n\nThis is presumably part of a larger struct, together"
        " with other nearby data.\n\ntype: struct monster_id_16",
    )

    HERO_NICKNAME = Symbol(
        [0x2AC75A],
        [0x22AC75A],
        0xA,
        "The hero's nickname.\n\nA null-terminated string, with a maximum length of 10."
        " Presumably encoded with the ANSI/Shift JIS encoding the game typically"
        " uses.\n\nThis is presumably part of a larger struct, together with other"
        " nearby data.",
    )

    PARTNER_SPECIES_ID = Symbol(
        [0x2AC768],
        [0x22AC768],
        0x2,
        "The partner's species ID.\n\nThis is presumably part of a larger struct,"
        " together with other nearby data.\n\ntype: struct monster_id_16",
    )

    LEADER_IQ_SKILLS = Symbol(
        [0x2B5AD8],
        [0x22B5AD8],
        0xC,
        "Unlocked IQ skills of the current leader, available for selection from the IQ"
        " skills menu.\n\nOne bit per skill (1 if unlocked). Same format as the IQ"
        " skills bitvector on the monster info struct.\n\nThis is presumably part of a"
        " larger struct, together with other nearby data.",
    )

    LEADER_NICKNAME = Symbol(
        [0x2B5AEA],
        [0x22B5AEA],
        0xA,
        "The current leader's nickname.\n\nA null-terminated string, with a maximum"
        " length of 10. Presumably encoded with the ANSI/Shift JIS encoding the game"
        " typically uses.\n\nThis is presumably part of a larger struct, together with"
        " other nearby data.",
    )

    PARTY_MEMBER_2_IQ_SKILLS = Symbol(
        [0x2B5B40],
        [0x22B5B40],
        0xC,
        "Unlocked IQ skills of the second party member, available for selection from"
        " the IQ skills menu.\n\nOne bit per skill (1 if unlocked). Same format as the"
        " IQ skills bitvector on the monster info struct.\n\nThis is presumably part of"
        " a larger struct, together with other nearby data.",
    )

    FRAMES_SINCE_LAUNCH_TIMES_THREE = Symbol(
        [0x2BA304],
        [0x22BA304],
        0x4,
        "Starts at 0 when the game is first launched, and ticks up by 3 per frame while"
        " the game is running.",
    )

    TURNING_ON_THE_SPOT_FLAG = Symbol(
        [0x37D5A6],
        [0x237D5A6],
        0x1,
        "[Runtime] Flag for whether the player is turning on the spot (pressing Y).",
    )

    FLOOR_GENERATION_STATUS = Symbol(
        [0x37DBBC],
        [0x237DBBC],
        0x40,
        "[Runtime] Status data related to generation of the current floor in a"
        " dungeon.\n\nThis data is populated as the dungeon floor is"
        " generated.\n\ntype: struct floor_generation_status",
    )


class EuRamSection:
    name = "ram"
    description = (
        "Main memory.\nData in this file aren't located in the ROM itself, and are"
        " instead constructs loaded at runtime.\n\nMore specifically, this file is a"
        " dumping ground for addresses that are useful to know about, but don't fall in"
        " the address ranges of any of the other files. Dynamically loaded constructs"
        " that do fall within the address range of a relevant binary should be listed"
        " in the corresponding YAML file of that binary, since it still has direct"
        " utility when reverse-engineering that particular binary."
    )
    loadaddress = 0x2000000
    length = 0x400000
    functions = EuRamFunctions
    data = EuRamData


class EuOverlay35Functions:
    pass


class EuOverlay35Data:
    pass


class EuOverlay35Section:
    name = "overlay35"
    description = "Unused; all zeroes."
    loadaddress = 0x22BD3C0
    length = 0x20
    functions = EuOverlay35Functions
    data = EuOverlay35Data


class EuOverlay33Functions:
    pass


class EuOverlay33Data:
    pass


class EuOverlay33Section:
    name = "overlay33"
    description = "Unused; all zeroes."
    loadaddress = 0x2383420
    length = 0x20
    functions = EuOverlay33Functions
    data = EuOverlay33Data


class EuSections:
    overlay20 = EuOverlay20Section

    overlay3 = EuOverlay3Section

    overlay8 = EuOverlay8Section

    overlay5 = EuOverlay5Section

    overlay17 = EuOverlay17Section

    overlay19 = EuOverlay19Section

    overlay12 = EuOverlay12Section

    overlay2 = EuOverlay2Section

    overlay28 = EuOverlay28Section

    overlay29 = EuOverlay29Section

    overlay11 = EuOverlay11Section

    overlay25 = EuOverlay25Section

    arm9 = EuArm9Section

    overlay0 = EuOverlay0Section

    overlay10 = EuOverlay10Section

    overlay34 = EuOverlay34Section

    overlay1 = EuOverlay1Section

    overlay4 = EuOverlay4Section

    overlay6 = EuOverlay6Section

    overlay7 = EuOverlay7Section

    overlay9 = EuOverlay9Section

    overlay30 = EuOverlay30Section

    overlay31 = EuOverlay31Section

    overlay13 = EuOverlay13Section

    overlay14 = EuOverlay14Section

    overlay15 = EuOverlay15Section

    overlay16 = EuOverlay16Section

    overlay18 = EuOverlay18Section

    overlay21 = EuOverlay21Section

    overlay22 = EuOverlay22Section

    overlay23 = EuOverlay23Section

    overlay24 = EuOverlay24Section

    overlay26 = EuOverlay26Section

    overlay27 = EuOverlay27Section

    overlay32 = EuOverlay32Section

    ram = EuRamSection

    overlay35 = EuOverlay35Section

    overlay33 = EuOverlay33Section

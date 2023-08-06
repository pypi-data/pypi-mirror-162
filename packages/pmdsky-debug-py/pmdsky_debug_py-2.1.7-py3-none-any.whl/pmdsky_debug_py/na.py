from .protocol import Symbol


class NaOverlay20Functions:
    pass


class NaOverlay20Data:
    RECYCLE_MENU_CONFIRM_1 = Symbol([0x2E44], [0x238CF84], 0x18, "")

    RECYCLE_MENU_CONFIRM_2 = Symbol([0x2E5C], [0x238CF9C], 0x18, "")

    RECYCLE_SUBMENU_1 = Symbol([0x2E74], [0x238CFB4], 0x18, "")

    RECYCLE_SUBMENU_2 = Symbol([0x2E8C], [0x238CFCC], 0x20, "")

    RECYCLE_MAIN_MENU_1 = Symbol([0x2EAC], [0x238CFEC], 0x28, "")

    RECYCLE_MAIN_MENU_2 = Symbol([0x2F48], [0x238D088], 0x20, "")

    RECYCLE_MAIN_MENU_3 = Symbol([0x2FB8], [0x238D0F8], 0x18, "")


class NaOverlay20Section:
    name = "overlay20"
    description = "Controls the Recycle Shop."
    loadaddress = 0x238A140
    length = 0x3000
    functions = NaOverlay20Functions
    data = NaOverlay20Data


class NaOverlay3Functions:
    pass


class NaOverlay3Data:
    pass


class NaOverlay3Section:
    name = "overlay3"
    description = "Controls the Friend Rescue submenu within the top menu."
    loadaddress = 0x233CA80
    length = 0xA160
    functions = NaOverlay3Functions
    data = NaOverlay3Data


class NaOverlay8Functions:
    pass


class NaOverlay8Data:
    pass


class NaOverlay8Section:
    name = "overlay8"
    description = (
        "Controls the Send Demo Dungeon submenu within the top menu (under 'Other')."
    )
    loadaddress = 0x233CA80
    length = 0x2200
    functions = NaOverlay8Functions
    data = NaOverlay8Data


class NaOverlay5Functions:
    pass


class NaOverlay5Data:
    pass


class NaOverlay5Section:
    name = "overlay5"
    description = "Controls the Trade Team submenu within the top menu."
    loadaddress = 0x233CA80
    length = 0x3240
    functions = NaOverlay5Functions
    data = NaOverlay5Data


class NaOverlay17Functions:
    pass


class NaOverlay17Data:
    ASSEMBLY_MENU_CONFIRM = Symbol([0x1A44], [0x238BB84], 0x18, "")

    ASSEMBLY_MAIN_MENU_1 = Symbol([0x1A5C], [0x238BB9C], 0x18, "")

    ASSEMBLY_MAIN_MENU_2 = Symbol([0x1A74], [0x238BBB4], 0x20, "")

    ASSEMBLY_SUBMENU_1 = Symbol([0x1A94], [0x238BBD4], 0x28, "")

    ASSEMBLY_SUBMENU_2 = Symbol([0x1ABC], [0x238BBFC], 0x30, "")

    ASSEMBLY_SUBMENU_3 = Symbol([0x1AEC], [0x238BC2C], 0x30, "")

    ASSEMBLY_SUBMENU_4 = Symbol([0x1B1C], [0x238BC5C], 0x38, "")

    ASSEMBLY_SUBMENU_5 = Symbol([0x1B54], [0x238BC94], 0x38, "")

    ASSEMBLY_SUBMENU_6 = Symbol([0x1B8C], [0x238BCCC], 0x38, "")

    ASSEMBLY_SUBMENU_7 = Symbol([0x1BC4], [0x238BD04], 0x40, "")


class NaOverlay17Section:
    name = "overlay17"
    description = "Controls the Chimecho Assembly."
    loadaddress = 0x238A140
    length = 0x1CE0
    functions = NaOverlay17Functions
    data = NaOverlay17Data


class NaOverlay19Functions:
    pass


class NaOverlay19Data:
    BAR_MENU_CONFIRM_1 = Symbol([0x40C8], [0x238E208], 0x18, "")

    BAR_MENU_CONFIRM_2 = Symbol([0x40E0], [0x238E220], 0x18, "")

    BAR_MAIN_MENU = Symbol([0x4110], [0x238E250], 0x20, "")

    BAR_SUBMENU_1 = Symbol([0x4130], [0x238E270], 0x20, "")

    BAR_SUBMENU_2 = Symbol([0x4150], [0x238E290], 0x30, "")


class NaOverlay19Section:
    name = "overlay19"
    description = "Controls Spinda's Juice Bar."
    loadaddress = 0x238A140
    length = 0x4240
    functions = NaOverlay19Functions
    data = NaOverlay19Data


class NaOverlay12Functions:
    pass


class NaOverlay12Data:
    pass


class NaOverlay12Section:
    name = "overlay12"
    description = "Unused; all zeroes."
    loadaddress = 0x238A140
    length = 0x20
    functions = NaOverlay12Functions
    data = NaOverlay12Data


class NaOverlay2Functions:
    pass


class NaOverlay2Data:
    pass


class NaOverlay2Section:
    name = "overlay2"
    description = (
        "Controls the Nintendo WFC Settings interface, accessed from the top menu"
        " (Other > Nintendo WFC > Nintendo WFC Settings). Presumably contains code for"
        " Nintendo Wi-Fi setup."
    )
    loadaddress = 0x2329520
    length = 0x2AFA0
    functions = NaOverlay2Functions
    data = NaOverlay2Data


class NaOverlay28Functions:
    pass


class NaOverlay28Data:
    pass


class NaOverlay28Section:
    name = "overlay28"
    description = "Controls the staff credits sequence."
    loadaddress = 0x238A140
    length = 0xC60
    functions = NaOverlay28Functions
    data = NaOverlay28Data


class NaOverlay29Functions:
    DungeonAlloc = Symbol(
        [0x281C],
        [0x22DEA5C],
        None,
        "Allocates a new dungeon struct.\n\nThis updates the master dungeon pointer and"
        " returns a copy of that pointer.\n\nreturn: pointer to a newly allocated"
        " dungeon struct",
    )

    GetDungeonPtrMaster = Symbol(
        [0x2840],
        [0x22DEA80],
        None,
        "Returns the master dungeon pointer (a global, see"
        " DUNGEON_PTR_MASTER).\n\nreturn: pointer to a newly allocated dungeon struct",
    )

    DungeonZInit = Symbol(
        [0x2850],
        [0x22DEA90],
        None,
        "Zero-initializes the dungeon struct pointed to by the master dungeon"
        " pointer.\n\nNo params.",
    )

    DungeonFree = Symbol(
        [0x2870],
        [0x22DEAB0],
        None,
        "Frees the dungeons struct pointer to by the master dungeon pointer, and"
        " nullifies the pointer.\n\nNo params.",
    )

    RunDungeon = Symbol(
        [0x2CF8],
        [0x22DEF38],
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
            0x70A8,
            0x7578,
            0xD3B4,
            0x103C8,
            0x10B80,
            0x12108,
            0x13560,
            0x14350,
            0x1904C,
            0x1A068,
            0x1B124,
            0x2075C,
            0x22B58,
            0x23EA4,
            0x267F8,
            0x28578,
            0x2934C,
            0x299C4,
            0x2BCB8,
            0x2C03C,
            0x2CD7C,
            0x326B0,
            0x32DC8,
            0x34DD0,
            0x35674,
            0x38ED8,
            0x3CAF4,
            0x3CC0C,
            0x3DD4C,
            0x3EF54,
            0x40988,
            0x42B98,
            0x43330,
            0x439BC,
            0x43F3C,
            0x44524,
            0x451F8,
            0x493E0,
            0x4BDCC,
            0x4E198,
            0x502C0,
            0x52010,
            0x52600,
            0x57D6C,
            0x58E98,
            0x5BA68,
            0x688B8,
            0x69458,
            0x6B964,
            0x6D63C,
            0x71B90,
            0x729D4,
        ],
        [
            0x22E0354,
            0x22E1A1C,
            0x22E32E8,
            0x22E37B8,
            0x22E95F4,
            0x22EC608,
            0x22ECDC0,
            0x22EE348,
            0x22EF7A0,
            0x22F0590,
            0x22F528C,
            0x22F62A8,
            0x22F7364,
            0x22FC99C,
            0x22FED98,
            0x23000E4,
            0x2302A38,
            0x23047B8,
            0x230558C,
            0x2305C04,
            0x2307EF8,
            0x230827C,
            0x2308FBC,
            0x230E8F0,
            0x230F008,
            0x2311010,
            0x23118B4,
            0x2315118,
            0x2318D34,
            0x2318E4C,
            0x2319F8C,
            0x231B194,
            0x231CBC8,
            0x231EDD8,
            0x231F570,
            0x231FBFC,
            0x232017C,
            0x2320764,
            0x2321438,
            0x2325620,
            0x232800C,
            0x232A3D8,
            0x232C500,
            0x232E250,
            0x232E840,
            0x2333FAC,
            0x23350D8,
            0x2337CA8,
            0x2344AF8,
            0x2345698,
            0x2347BA4,
            0x234987C,
            0x234DDD0,
            0x234EC14,
        ],
        None,
        "Checks if an entity pointer points to a valid entity (not entity type 0, which"
        " represents no entity).\n\nr0: entity pointer\nreturn: bool",
    )

    GetFloorType = Symbol(
        [0x4170],
        [0x22E03B0],
        None,
        "Get the current floor type.\n\nFloor types:\n  0 appears to mean the current"
        " floor is 'normal'\n  1 appears to mean the current floor is a fixed floor\n "
        " 2 means the current floor has a rescue point\n\nreturn: floor type",
    )

    TryForcedLoss = Symbol(
        [0x43E0],
        [0x22E0620],
        None,
        "Attempts to trigger a forced loss of the type specified in"
        " dungeon::forced_loss_reason.\n\nr0: if true, the function will not check for"
        " the end of the floor condition and will skip other (unknown) actions in case"
        " of forced loss.\nreturn: true if the forced loss happens, false otherwise",
    )

    FixedRoomIsSubstituteRoom = Symbol(
        [0x468C],
        [0x22E08CC],
        None,
        "Checks if the current fixed room is the 'substitute room' (ID"
        " 0x6E).\n\nreturn: bool",
    )

    StoryRestrictionsEnabled = Symbol(
        [0x46E8],
        [0x22E0928],
        None,
        "Returns true if certain special restrictions are enabled.\n\nIf true, you will"
        " get kicked out of the dungeon if a team member that passes the"
        " arm9::JoinedAtRangeCheck2 check faints.\n\nreturn: !dungeon::nonstory_flag ||"
        " dungeon::hidden_land_flag",
    )

    FadeToBlack = Symbol(
        [0x4728],
        [0x22E0968],
        None,
        "Fades the screen to black across several frames.\n\nNo params.",
    )

    GetTileAtEntity = Symbol(
        [0x53E8],
        [0x22E1628],
        None,
        "Returns a pointer to the tile where an entity is located.\n\nr0: pointer to"
        " entity\nreturns: pointer to tile",
    )

    CanTargetEntity = Symbol(
        [0x65D0],
        [0x22E2810],
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
        [0x22E2954],
        None,
        "Checks if a monster can target a position. This function just calls"
        " IsPositionInSight using the position of the user as the origin.\n\nr0: Entity"
        " pointer\nr1: Target position\nreturn: True if the specified monster can"
        " target the target position, false otherwise.",
    )

    SubstitutePlaceholderStringTags = Symbol(
        [0x6898],
        [0x22E2AD8],
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
        [0x6B98],
        [0x22E2DD8],
        None,
        "Sets the Map Surveyor flag in the dungeon struct to true if a team member has"
        " Map Surveyor, sets it to false otherwise.\n\nThis function has two variants:"
        " in the EU ROM, it will return true if the flag was changed. The NA version"
        " will return the new value of the flag instead.\n\nreturn: bool",
    )

    ItemIsActive = Symbol(
        [
            0x70CC,
            0x120D8,
            0x19754,
            0x23658,
            0x2648C,
            0x2BCDC,
            0x2E79C,
            0x32338,
            0x335D0,
            0x34DF4,
            0x359B8,
            0x38EFC,
            0x6B910,
        ],
        [
            0x22E330C,
            0x22EE318,
            0x22F5994,
            0x22FF898,
            0x23026CC,
            0x2307F1C,
            0x230A9DC,
            0x230E578,
            0x230F810,
            0x2311034,
            0x2311BF8,
            0x231513C,
            0x2347B50,
        ],
        None,
        "Checks if a monster is holding a certain item that isn't disabled by"
        " Klutz.\n\nr0: entity pointer\nr1: item ID\nreturn: bool",
    )

    UpdateStatusIconFlags = Symbol(
        [0x7874],
        [0x22E3AB4],
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
        [0xBB0C],
        [0x22E7D4C],
        None,
        "Returns true if the specified monster is included in the floor's monster spawn"
        " list (the modified list after a maximum of 14 different species were chosen,"
        " not the raw list read from the mappa file).\n\nr0: Monster ID\nreturn: bool",
    )

    GetMonsterIdToSpawn = Symbol(
        [0xBB60],
        [0x22E7DA0],
        None,
        "Get the id of the monster to be randomly spawned.\n\nr0: the spawn weight to"
        " use (0 for normal, 1 for monster house)\nreturn: monster ID",
    )

    GetMonsterLevelToSpawn = Symbol(
        [0xBC18],
        [0x22E7E58],
        None,
        "Get the level of the monster to be spawned, given its id.\n\nr0: monster"
        " ID\nreturn: Level of the monster to be spawned, or 1 if the specified ID"
        " can't be found on the floor's spawn table.",
    )

    GetDirectionTowardsPosition = Symbol(
        [0xCDE0],
        [0x22E9020],
        None,
        "Gets the direction in which a monster should move to go from the origin"
        " position to the target position\n\nr0: Origin position\nr1: Target"
        " position\nreturn: Direction in which to move to reach the target position"
        " from the origin position",
    )

    GetChebyshevDistance = Symbol(
        [0xCE4C],
        [0x22E908C],
        None,
        "Returns the Chebyshev distance between two positions. Calculated as"
        " max(abs(x0-x1), abs(y0-y1)).\n\nr0: Position A\nr1: Position B\nreturn:"
        " Chebyshev Distance between position A and position B",
    )

    IsPositionInSight = Symbol(
        [0xCF64],
        [0x22E91A4],
        None,
        "Checks if a given target position is in sight from a given origin"
        " position.\nThere's multiple factors that affect this check, but generally,"
        " it's true if both positions are in the same room or within 2 tiles of each"
        " other.\n\nr0: Origin position\nr1: Target position\nr2: True to assume the"
        " entity standing on the origin position has the dropeye status\nreturn: True"
        " if the target position is in sight from the origin position",
    )

    GetLeader = Symbol(
        [0xD340],
        [0x22E9580],
        None,
        "Gets the pointer to the entity that is currently leading the team, or null if"
        " none of the first 4 entities is a valid monster with its is_team_leader flag"
        " set. It also sets LEADER_PTR to the result before returning it.\n\nreturn:"
        " Pointer to the current leader of the team or null if there's no valid"
        " leader.",
    )

    TickStatusTurnCounter = Symbol(
        [0xD804],
        [0x22E9A44],
        None,
        "Ticks down a turn counter for a status condition. If the counter equals 0x7F,"
        " it will not be decreased.\n\nr0: pointer to the status turn counter\nreturn:"
        " new counter value",
    )

    AdvanceFrame = Symbol(
        [0xDDA0],
        [0x22E9FE0],
        None,
        "Advances one frame. Does not return until the next frame starts.\n\nr0: ? -"
        " Unused by the function",
    )

    GenerateDungeonRngSeed = Symbol(
        [0xE740],
        [0x22EA980],
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
        [0xE78C],
        [0x22EA9CC],
        None,
        "Gets the current preseed stored in the global dungeon PRNG state. See"
        " GenerateDungeonRngSeed for more information.\n\nreturn: current dungeon RNG"
        " preseed",
    )

    SetDungeonRngPreseed = Symbol(
        [0xE79C],
        [0x22EA9DC],
        None,
        "Sets the preseed in the global dungeon PRNG state. See GenerateDungeonRngSeed"
        " for more information.\n\nr0: preseed",
    )

    InitDungeonRng = Symbol(
        [0xE7AC],
        [0x22EA9EC],
        None,
        "Initialize (or reinitialize) the dungeon PRNG with a given seed. The primary"
        " LCG and the five secondary LCGs are initialized jointly, and with the same"
        " seed.\n\nr0: seed",
    )

    DungeonRand16Bit = Symbol(
        [0xE7E0],
        [0x22EAA20],
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
        [0xE858],
        [0x22EAA98],
        None,
        "Compute a pseudorandom integer under a given maximum value using the dungeon"
        " PRNG.\n\nr0: high\nreturn: pseudorandom integer on the interval [0, high"
        " - 1]",
    )

    DungeonRandRange = Symbol(
        [0xE880],
        [0x22EAAC0],
        None,
        "Compute a pseudorandom value between two integers using the dungeon"
        " PRNG.\n\nr0: x\nr1: y\nreturn: pseudorandom integer on the interval [min(x,"
        " y), max(x, y) - 1]",
    )

    DungeonRandOutcome = Symbol(
        [0xE8E0, 0xE910],
        [0x22EAB20, 0x22EAB50],
        None,
        "Returns the result of a possibly biased coin flip (a Bernoulli random"
        " variable) with some success probability p, using the dungeon PRNG.\n\nr0:"
        " success percentage (100*p)\nreturn: true with probability p, false with"
        " probability (1-p)",
    )

    CalcStatusDuration = Symbol(
        [0xE940],
        [0x22EAB80],
        None,
        "Seems to calculate the duration of a volatile status on a monster.\n\nr0:"
        " entity pointer\nr1: pointer to a turn range (an array of two shorts {lower,"
        " higher})\nr2: flag for whether or not to factor in the Self Curer IQ skill"
        " and the Natural Cure ability\nreturn: number of turns for the status"
        " condition",
    )

    DungeonRngUnsetSecondary = Symbol(
        [0xE9F4],
        [0x22EAC34],
        None,
        "Sets the dungeon PRNG to use the primary LCG for subsequent random number"
        " generation, and also resets the secondary LCG index back to 0.\n\nSimilar to"
        " DungeonRngSetPrimary, but DungeonRngSetPrimary doesn't modify the secondary"
        " LCG index if it was already set to something other than 0.\n\nNo params.",
    )

    DungeonRngSetSecondary = Symbol(
        [0xEA0C],
        [0x22EAC4C],
        None,
        "Sets the dungeon PRNG to use one of the 5 secondary LCGs for subsequent random"
        " number generation.\n\nr0: secondary LCG index",
    )

    DungeonRngSetPrimary = Symbol(
        [0xEA24],
        [0x22EAC64],
        None,
        "Sets the dungeon PRNG to use the primary LCG for subsequent random number"
        " generation.\n\nNo params.",
    )

    TrySwitchPlace = Symbol(
        [0xEF38],
        [0x22EB178],
        None,
        "The user entity attempts to switch places with the target entity (i.e. by the"
        " effect of the Switcher Orb). \n\nThe function checks for the Suction Cups"
        " ability for both the user and the target, and for the Mold Breaker ability on"
        " the user.\n\nr0: pointer to user entity\nr1: pointer to target entity",
    )

    ClearMonsterActionFields = Symbol(
        [0xF1B4],
        [0x22EB3F4],
        None,
        "Clears the fields related to AI in the monster's data struct, setting them all"
        " to 0.\nSpecifically, monster::action_id, monster::action_use_idx and"
        " monster::field_0x54 are cleared.\n\nr0: Pointer to the monster's action_id"
        " field (this field is probably contained in a struct)",
    )

    SetMonsterActionFields = Symbol(
        [0xF1C8],
        [0x22EB408],
        None,
        "Sets some the fields related to AI in the monster's data"
        " struct.\nSpecifically, monster::action_id, monster::action_use_idx and"
        " monster::field_0x54. The last 2 are always set to 0.\n\nr0: Pointer to the"
        " monster's action_id field (this field is probably contained in a struct)\nr1:"
        " Value to set monster::action_id to.",
    )

    SetActionPassTurnOrWalk = Symbol(
        [0xF1DC],
        [0x22EB41C],
        None,
        "Sets a monster's action to action::ACTION_PASS_TURN or action::ACTION_WALK,"
        " depending on the result of GetCanMoveFlag for the monster's ID.\n\nr0:"
        " Pointer to the monster's action_id field (this field is probably contained in"
        " a struct)\nr1: Monster ID",
    )

    SetActionRegularAttack = Symbol(
        [0xFA10],
        [0x22EBC50],
        None,
        "Sets a monster's action to action::ACTION_REGULAR_ATTACK, with a specified"
        " direction.\n\nr0: Pointer to the monster's action_id field (this field is"
        " probably contained in a struct)\nr1: Direction in which to use the move. Gets"
        " stored in monster::direction.",
    )

    SetActionUseMoveAi = Symbol(
        [0xFA7C],
        [0x22EBCBC],
        None,
        "Sets a monster's action to action::ACTION_USE_MOVE_AI, with a specified"
        " direction and move index.\n\nr0: Pointer to the monster's action_id field"
        " (this field is probably contained in a struct)\nr1: Index of the move to use"
        " (0-3). Gets stored in monster::action_use_idx.\nr2: Direction in which to use"
        " the move. Gets stored in monster::direction.",
    )

    RunFractionalTurn = Symbol(
        [0xFAC8],
        [0x22EBD08],
        None,
        "The main function which executes the actions that take place in a fractional"
        " turn. Called in a loop by RunDungeon while IsFloorOver returns false.\n\nr0:"
        " first loop flag (true when the function is first called during a floor)",
    )

    RunLeaderTurn = Symbol(
        [0x100C8],
        [0x22EC308],
        None,
        "Handles the leader's turn. Includes a movement speed check that might cause it"
        " to return early if the leader isn't fast enough to act in this fractional"
        " turn. If that check (and some others) pass, the function does not return"
        " until the leader performs an action.\n\nr0: ?\nreturn: true if the leader has"
        " performed an action",
    )

    TrySpawnMonsterAndActivatePlusMinus = Symbol(
        [0x1049C],
        [0x22EC6DC],
        None,
        "Called at the beginning of RunFractionalTurn. Executed only if"
        " FRACTIONAL_TURN_SEQUENCE[fractional_turn * 2] is not 0.\n\nFirst it calls"
        " TrySpawnMonsterAndTickSpawnCounter, then tries to activate the Plus and Minus"
        " abilities for both allies and enemies, and finally calls TryForcedLoss.\n\nNo"
        " params.",
    )

    IsFloorOver = Symbol(
        [0x105A8],
        [0x22EC7E8],
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
        [0x10908],
        [0x22ECB48],
        None,
        "Decrements dungeon::wind_turns and displays a wind warning message if"
        " required.\n\nNo params.",
    )

    SetForcedLossReason = Symbol(
        [0x10DC8],
        [0x22ED008],
        None,
        "Sets dungeon::forced_loss_reason to the specified value\n\nr0: Forced loss"
        " reason",
    )

    GetForcedLossReason = Symbol(
        [0x10DDC],
        [0x22ED01C],
        None,
        "Returns dungeon::forced_loss_reason\n\nreturn: forced_loss_reason",
    )

    ResetDamageDesc = Symbol(
        [0x1ABD8],
        [0x22F6E18],
        None,
        "Seems to zero some damage description struct, which is output by the damage"
        " calculation function.\n\nr0: damage description pointer",
    )

    GetSpriteIndex = Symbol(
        [0x1B148],
        [0x22F7388],
        None,
        "Gets the sprite index of the specified monster on this floor\n\nr0: Monster"
        " ID\nreturn: Sprite index of the specified monster ID",
    )

    JoinedAtRangeCheck2Veneer = Symbol(
        [0x1B168],
        [0x22F73A8],
        None,
        "Likely a linker-generated veneer for arm9::JoinedAtRangeCheck2.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nNo"
        " params.",
    )

    FloorNumberIsEven = Symbol(
        [0x1B174],
        [0x22F73B4],
        None,
        "Checks if the current dungeon floor number is even.\n\nHas a special check to"
        " return false for Labyrinth Cave B10F (the Gabite boss fight).\n\nreturn:"
        " bool",
    )

    GetKecleonIdToSpawnByFloor = Symbol(
        [0x1B1AC],
        [0x22F73EC],
        None,
        "If the current floor number is even, returns female Kecleon's id (0x3D7),"
        " otherwise returns male Kecleon's id (0x17F).\n\nreturn: monster ID",
    )

    LoadMonsterSprite = Symbol(
        [0x1B414],
        [0x22F7654],
        None,
        "Loads the sprite of the specified monster to use it in a dungeon.\n\nr0:"
        " Monster id\nr1: ?",
    )

    EuFaintCheck = Symbol(
        None,
        None,
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
        [0x1BCF0],
        [0x22F7F30],
        None,
        "Handles a fainted pokémon (reviving does not count as fainting).\n\nr0:"
        " Fainted entity\nr1: Faint reason (move ID or greater than the max move id for"
        " other causes)\nr2: Entity responsible of the fainting",
    )

    UpdateAiTargetPos = Symbol(
        [0x1CF04],
        [0x22F9144],
        None,
        "Given a monster, updates its target_pos field based on its current position"
        " and the direction in which it plans to attack.\n\nr0: Entity pointer",
    )

    TryActivateSlowStart = Symbol(
        [0x1CFFC],
        [0x22F923C],
        None,
        "Runs a check over all monsters on the field for the ability Slow Start, and"
        " lowers the speed of those who have it.\n\nNo params",
    )

    TryActivateArtificialWeatherAbilities = Symbol(
        [0x1D098],
        [0x22F92D8],
        None,
        "Runs a check over all monsters on the field for abilities that affect the"
        " weather and changes the floor's weather accordingly.\n\nNo params",
    )

    DefenderAbilityIsActive = Symbol(
        [
            0x1D48C,
            0x257CC,
            0x2E700,
            0x35954,
            0x46B24,
            0x4C3F4,
            0x4DCD4,
            0x4FB90,
            0x51BE0,
            0x567CC,
        ],
        [
            0x22F96CC,
            0x2301A0C,
            0x230A940,
            0x2311B94,
            0x2322D64,
            0x2328634,
            0x2329F14,
            0x232BDD0,
            0x232DE20,
            0x2332A0C,
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
            0x1D4E0,
            0x25820,
            0x2E754,
            0x33740,
            0x3C870,
            0x3E794,
            0x3F0D8,
            0x46B78,
            0x71220,
        ],
        [
            0x22F9720,
            0x2301A60,
            0x230A994,
            0x230F980,
            0x2318AB0,
            0x231A9D4,
            0x231B318,
            0x2322DB8,
            0x234D460,
        ],
        None,
        "Checks if an entity is a monster (entity type 1).\n\nr0: entity"
        " pointer\nreturn: bool",
    )

    TryActivateTruant = Symbol(
        [0x1D5B0],
        [0x22F97F0],
        None,
        "Checks if an entity has the ability Truant, and if so tries to apply the pause"
        " status to it.\n\nr0: pointer to entity",
    )

    RestorePpAllMovesSetFlags = Symbol(
        [0x1D834],
        [0x22F9A74],
        None,
        "Restores PP for all moves, clears flags move::f_consume_2_pp,"
        " move::flags2_unk5 and move::flags2_unk7, and sets flag"
        " move::f_consume_pp.\nCalled when a monster is revived.\n\nr0: pointer to"
        " entity whose moves will be restored",
    )

    ShouldMonsterHeadToStairs = Symbol(
        [0x1E1F0],
        [0x22FA430],
        None,
        "Checks if a given monster should try to reach the stairs when controlled by"
        " the AI\n\nr0: Entity pointer\nreturn: True if the monster should try to reach"
        " the stairs, false otherwise",
    )

    MewSpawnCheck = Symbol(
        [0x1E3B0],
        [0x22FA5F0],
        None,
        "If the monster id parameter is 0x97 (Mew), returns false if either"
        " dungeon::mew_cannot_spawn or the second parameter are true.\n\nCalled before"
        " spawning an enemy, appears to be checking if Mew can spawn on the current"
        " floor.\n\nr0: monster id\nr1: return false if the monster id is Mew\nreturn:"
        " bool",
    )

    ExclusiveItemEffectIsActive = Symbol(
        [
            0x1EA58,
            0x23CE8,
            0x2E778,
            0x3366C,
            0x34E24,
            0x385AC,
            0x3D568,
            0x3E63C,
            0x476D8,
            0x567A8,
            0x6B940,
            0x6C070,
        ],
        [
            0x22FAC98,
            0x22FFF28,
            0x230A9B8,
            0x230F8AC,
            0x2311064,
            0x23147EC,
            0x23197A8,
            0x231A87C,
            0x2323918,
            0x23329E8,
            0x2347B80,
            0x23482B0,
        ],
        None,
        "Checks if a monster is a team member under the effects of a certain exclusive"
        " item effect.\n\nr0: entity pointer\nr1: exclusive item effect ID\nreturn:"
        " bool",
    )

    GetTeamMemberWithIqSkill = Symbol(
        [0x1EDB8],
        [0x22FAFF8],
        None,
        "Returns an entity pointer to the first team member which has the specified iq"
        " skill.\n\nr0: iq skill id\nreturn: pointer to entity",
    )

    TeamMemberHasEnabledIqSkill = Symbol(
        [0x1EE24],
        [0x22FB064],
        None,
        "Returns true if any team member has the specified iq skill.\n\nr0: iq skill"
        " id\nreturn: bool",
    )

    TeamLeaderIqSkillIsEnabled = Symbol(
        [0x1EE40],
        [0x22FB080],
        None,
        "Returns true the leader has the specified iq skill.\n\nr0: iq skill"
        " id\nreturn: bool",
    )

    HasLowHealth = Symbol(
        [0x1F3D0],
        [0x22FB610],
        None,
        "Checks if the entity passed is a valid monster, and if it's at low health"
        " (below 25% rounded down)\n\nr0: entity pointer\nreturn: bool",
    )

    IsSpecialStoryAlly = Symbol(
        [0x1F890],
        [0x22FBAD0],
        None,
        "Checks if a monster is a special story ally.\n\nThis is a hard-coded check"
        " that looks at the monster's 'Joined At' field. If the value is in the range"
        " [DUNGEON_JOINED_AT_BIDOOF, DUNGEON_DUMMY_0xE3], this check will return"
        " true.\n\nr0: monster pointer\nreturn: bool",
    )

    IsExperienceLocked = Symbol(
        [0x1F8B0],
        [0x22FBAF0],
        None,
        "Checks if a monster does not gain experience.\n\nThis basically just inverts"
        " IsSpecialStoryAlly, with the exception of also checking for the 'Joined At'"
        " field being DUNGEON_CLIENT (is this set for mission clients?).\n\nr0: monster"
        " pointer\nreturn: bool",
    )

    InitTeam = Symbol(
        [0x202CC],
        [0x22FC50C],
        None,
        "Seems to initialize the team when entering a dungeon.\n\nr0: ?",
    )

    SpawnMonster = Symbol(
        [0x20E44],
        [0x22FD084],
        None,
        "Spawns the given monster on a tile.\n\nr0: pointer to struct"
        " spawned_monster_data\nr1: if true, the monster cannot spawn asleep, otherwise"
        " it will randomly be asleep\nreturn: pointer to entity",
    )

    InitTeamMember = Symbol(
        [0x21174],
        [0x22FD3B4],
        None,
        "Initializes a team member. Run at the start of each floor in a dungeon.\n\nr0:"
        " Monster ID\nr1: First type\nr2: Second type\nr3: Pointer to the struct"
        " containing the data of the team member to initialize\nstack[0]: ?\nstack[1]:"
        " ?\nstack[2]: ?\nstack[3]: ?\nstack[4]: ?",
    )

    ExecuteMonsterAction = Symbol(
        [0x2227C],
        [0x22FE4BC],
        None,
        "Executes the set action for the specified monster. Used for both AI actions"
        " and player-inputted actions. If the action is not ACTION_NOTHING,"
        " ACTION_PASS_TURN, ACTION_WALK or ACTION_UNK_4, the monster's already_acted"
        " field is set to true. Includes a switch based on the action ID that performs"
        " the action, although some of them aren't handled by said swtich.\n\nr0:"
        " Pointer to monster entity",
    )

    HasStatusThatPreventsActing = Symbol(
        [0x22F88],
        [0x22FF1C8],
        None,
        "Returns true if the monster has any status problem that prevents it from"
        " acting\n\nr0: Entity pointer\nreturn: True if the specified monster can't act"
        " because of a status problem, false otherwise.",
    )

    CalcSpeedStage = Symbol(
        [0x23BB4],
        [0x22FFDF4],
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
        [0x23D0C],
        [0x22FFF4C],
        None,
        "Calls CalcSpeedStage with a speed counter weight of 1.\n\nr0: pointer to"
        " entity\nreturn: speed stage",
    )

    GetNumberOfAttacks = Symbol(
        [0x23D1C],
        [0x22FFF5C],
        None,
        "Returns the number of attacks that a monster can do in one turn (1 or"
        " 2).\n\nChecks for the abilities Swift Swim, Chlorophyll, Unburden, and for"
        " exclusive items.\n\nr0: pointer to entity\nreturns: int",
    )

    SprintfStatic = Symbol(
        [0x24088],
        [0x23002C8],
        None,
        "Statically defined copy of sprintf(3) in overlay 29. See arm9.yml for more"
        " information.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )

    IsMonsterCornered = Symbol(
        [0x24ED8],
        [0x2301118],
        None,
        "True if the given monster is cornered (it can't move in any direction)\n\nr0:"
        " Entity pointer\nreturn: True if the monster can't move in any direction,"
        " false otherwise.",
    )

    CanAttackInDirection = Symbol(
        [0x24FF4],
        [0x2301234],
        None,
        "Returns whether a monster can attack in a given direction.\nThe check fails if"
        " the destination tile is impassable, contains a monster that isn't of type"
        " entity_type::ENTITY_MONSTER or if the monster can't directly move from the"
        " current tile into the destination tile.\n\nr0: Entity pointer\nr1:"
        " Direction\nreturn: True if the monster can attack into the tile adjacent to"
        " them in the specified direction, false otherwise.",
    )

    CanAiMonsterMoveInDirection = Symbol(
        [0x250B8],
        [0x23012F8],
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
        [0x25378],
        [0x23015B8],
        None,
        "Checks if a monster should run away from other monsters\n\nr0: Entity"
        " pointer\nreturn: True if the monster should run away, false otherwise",
    )

    ShouldMonsterRunAwayVariation = Symbol(
        [0x25468],
        [0x23016A8],
        None,
        "Calls ShouldMonsterRunAway and returns its result. It also calls another"
        " function if the result was true.\n\nr0: Entity pointer\nr1: ?\nreturn: Result"
        " of the call to ShouldMonsterRunAway",
    )

    NoGastroAcidStatus = Symbol(
        [0x25A9C],
        [0x2301CDC],
        None,
        "Checks if a monster does not have the Gastro Acid status.\n\nr0: entity"
        " pointer\nreturn: bool",
    )

    AbilityIsActive = Symbol(
        [0x25AD0],
        [0x2301D10],
        None,
        "Checks if a monster has a certain ability that isn't disabled by Gastro"
        " Acid.\n\nr0: entity pointer\nr1: ability ID\nreturn: bool",
    )

    LevitateIsActive = Symbol(
        [0x25BD8],
        [0x2301E18],
        None,
        "Checks if a monster is levitating (has the effect of Levitate and Gravity is"
        " not active).\n\nr0: pointer to entity\nreturn: bool",
    )

    MonsterIsType = Symbol(
        [0x25C10],
        [0x2301E50],
        None,
        "Checks if a monster is a given type.\n\nr0: entity pointer\nr1: type"
        " ID\nreturn: bool",
    )

    CanSeeInvisibleMonsters = Symbol(
        [0x25CAC],
        [0x2301EEC],
        None,
        "Returns whether a certain monster can see other invisible monsters.\nTo be"
        " precise, this function returns true if the monster is holding Goggle Specs or"
        " if it has the status status::STATUS_EYEDROPS.\n\nr0: Entity pointer\nreturn:"
        " True if the monster can see invisible monsters.",
    )

    HasDropeyeStatus = Symbol(
        [0x25D10],
        [0x2301F50],
        None,
        "Returns whether a certain monster is under the effect of"
        " status::STATUS_DROPEYE.\n\nr0: Entity pointer\nreturn: True if the monster"
        " has dropeye status.",
    )

    IqSkillIsEnabled = Symbol(
        [0x25D40],
        [0x2301F80],
        None,
        "Checks if a monster has a certain IQ skill enabled.\n\nr0: entity pointer\nr1:"
        " IQ skill ID\nreturn: bool",
    )

    GetMoveTypeForMonster = Symbol(
        [0x2603C],
        [0x230227C],
        None,
        "Check the type of a move when used by a certain monster. Accounts for special"
        " cases such as Hidden Power, Weather Ball, the regular attack...\n\nr0: Entity"
        " pointer\nr1: Pointer to move data\nreturn: Type of the move",
    )

    GetMovePower = Symbol(
        [0x260DC],
        [0x230231C],
        None,
        "Gets the power of a move, factoring in Ginseng/Space Globe boosts.\n\nr0: user"
        " pointer\nr1: move pointer\nreturn: move power",
    )

    AddExpSpecial = Symbol(
        [0x262FC],
        [0x230253C],
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
        [0x264BC],
        [0x23026FC],
        None,
        "Checks if the specified enemy should evolve because it just defeated an ally,"
        " and if so, attempts to evolve it.\n\nr0: Pointer to the enemy to check",
    )

    EvolveMonster = Symbol(
        [0x27A3C],
        [0x2303C7C],
        None,
        "Makes the specified monster evolve into the specified species.\n\nr0: Pointer"
        " to the entity to evolve\nr1: ?\nr2: Species to evolve into",
    )

    GetSleepAnimationId = Symbol(
        [0x28874],
        [0x2304AB4],
        None,
        "Returns the animation id to be applied to a monster that has the sleep,"
        " napping, nightmare or bide status.\n\nReturns a different animation for"
        " sudowoodo and for monsters with infinite sleep turns (0x7F).\n\nr0: pointer"
        " to entity\nreturn: animation ID",
    )

    DisplayActions = Symbol(
        [0x28DA0],
        [0x2304FE0],
        None,
        "Graphically displays any pending actions that have happened but haven't been"
        " shown on screen yet. All actions are displayed at the same time. For example,"
        " this delayed display system is used to display multiple monsters moving at"
        " once even though they take turns sequentially.\n\nr0: Pointer to an entity."
        " Can be null.\nreturns: Seems to be true if there were any pending actions to"
        " display.",
    )

    EndFrozenClassStatus = Symbol(
        [0x2A018],
        [0x2306258],
        None,
        "Cures the target's freeze, shadow hold, ingrain, petrified, constriction or"
        " wrap (both as user and as target) status due to the action of the"
        " user.\n\nr0: pointer to user\nr1: pointer to target\nr2: if true, the event"
        " will be printed to the log",
    )

    EndCringeClassStatus = Symbol(
        [0x2A194],
        [0x23063D4],
        None,
        "Cures the target's cringe, confusion, cowering, pause, taunt, encore or"
        " infatuated status due to the action of the user, and prints the event to the"
        " log.\n\nr0: pointer to user\nr1: pointer to target",
    )

    RunMonsterAi = Symbol(
        [0x2C100],
        [0x2308340],
        None,
        "Runs the AI for a single monster to determine whether the monster can act and"
        " which action it should perform if so\n\nr0: Pointer to monster\nr1: ?",
    )

    ApplyDamage = Symbol(
        [0x2CDA0],
        [0x2308FE0],
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
        [0x2EA18],
        [0x230AC58],
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
        [0x2F96C],
        [0x230BBAC],
        None,
        "Probably the damage calculation function.\n\nr0: attacker pointer\nr1:"
        " defender pointer\nr2: attack type\nr3: attack power\nstack[0]: crit"
        " chance\nstack[1]: [output] struct containing info about the damage"
        " calculation\nstack[2]: damage multiplier (as a binary fixed-point number with"
        " 8 fraction bits)\nstack[3]: move ID\nstack[4]: ?",
    )

    CalcRecoilDamageFixed = Symbol(
        [0x30F4C],
        [0x230D18C],
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
        [0x31000],
        [0x230D240],
        None,
        "Appears to calculate damage from a fixed-damage effect.\n\nr0: attacker"
        " pointer\nr1: defender pointer\nr2: fixed damage\nr3: ?\nstack[0]: [output]"
        " struct containing info about the damage calculation\nstack[1]: attack"
        " type\nstack[2]: move category\nstack[3]: ?\nstack[4]: message"
        " type\nothers: ?",
    )

    CalcDamageFixedNoCategory = Symbol(
        [0x31168],
        [0x230D3A8],
        None,
        "A wrapper around CalcDamageFixed with the move category set to none.\n\nr0:"
        " attacker pointer\nr1: defender pointer\nr2: fixed damage\nstack[0]: [output]"
        " struct containing info about the damage calculation\nstack[1]: attack"
        " type\nothers: ?",
    )

    CalcDamageFixedWrapper = Symbol(
        [0x311B4],
        [0x230D3F4],
        None,
        "A wrapper around CalcDamageFixed.\n\nr0: attacker pointer\nr1: defender"
        " pointer\nr2: fixed damage\nstack[0]: [output] struct containing info about"
        " the damage calculation\nstack[1]: attack type\nstack[2]: move"
        " category\nothers: ?",
    )

    ResetDamageCalcScratchSpace = Symbol(
        [0x312E8],
        [0x230D528],
        None,
        "CalcDamage seems to use scratch space of some kind, which this function"
        " zeroes.\n\nNo params.",
    )

    TrySpawnMonsterAndTickSpawnCounter = Symbol(
        [0x3247C],
        [0x230E6BC],
        None,
        "First ticks up the spawn counter, and if it's equal or greater than the spawn"
        " cooldown, it will try to spawn an enemy if the number of enemies is below the"
        " spawn cap.\n\nIf the spawn counter is greater than 900, it will instead"
        " perform the special spawn caused by the ability Illuminate.\n\nNo params.",
    )

    AuraBowIsActive = Symbol(
        [0x33488],
        [0x230F6C8],
        None,
        "Checks if a monster is holding an aura bow that isn't disabled by"
        " Klutz.\n\nr0: entity pointer\nreturn: bool",
    )

    ExclusiveItemOffenseBoost = Symbol(
        [0x33538],
        [0x230F778],
        None,
        "Gets the exclusive item boost for attack/special attack for a monster\n\nr0:"
        " entity pointer\nr1: move category index (0 for physical, 1 for"
        " special)\nreturn: boost",
    )

    ExclusiveItemDefenseBoost = Symbol(
        [0x33548],
        [0x230F788],
        None,
        "Gets the exclusive item boost for defense/special defense for a monster\n\nr0:"
        " entity pointer\nr1: move category index (0 for physical, 1 for"
        " special)\nreturn: boost",
    )

    TickNoSlipCap = Symbol(
        [0x33950],
        [0x230FB90],
        None,
        "Checks if the entity is a team member and holds the No-Slip Cap, and if so"
        " attempts to make one item in the bag sticky.\n\nr0: pointer to entity",
    )

    TickStatusAndHealthRegen = Symbol(
        [0x34E48],
        [0x2311088],
        None,
        "Applies the natural HP regen effect by taking modifiers into account (Poison"
        " Heal, Heal Ribbon, weather-related regen). Then it ticks down counters for"
        " volatile status effects, and heals them if the counter reached zero.\n\nr0:"
        " pointer to entity",
    )

    InflictSleepStatusSingle = Symbol(
        [0x355E4],
        [0x2311824],
        None,
        "This is called by TryInflictSleepStatus.\n\nr0: entity pointer\nr1: number of"
        " turns",
    )

    TryInflictSleepStatus = Symbol(
        [0x35698],
        [0x23118D8],
        None,
        "Inflicts the Sleep status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: number of turns\nr3: flag"
        " to log a message on failure",
    )

    TryInflictNightmareStatus = Symbol(
        [0x35A0C],
        [0x2311C4C],
        None,
        "Inflicts the Nightmare status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: number"
        " of turns",
    )

    TryInflictNappingStatus = Symbol(
        [0x35B20],
        [0x2311D60],
        None,
        "Inflicts the Napping status condition (from Rest) on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: number"
        " of turns",
    )

    TryInflictYawningStatus = Symbol(
        [0x35C30],
        [0x2311E70],
        None,
        "Inflicts the Yawning status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: number of turns",
    )

    TryInflictSleeplessStatus = Symbol(
        [0x35D40],
        [0x2311F80],
        None,
        "Inflicts the Sleepless status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    TryInflictPausedStatus = Symbol(
        [0x35E2C],
        [0x231206C],
        None,
        "Inflicts the Paused status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: ?\nr3: number of"
        " turns\nstack[0]: flag to log a message on failure\nstack[1]: flag to only"
        " perform the check for inflicting without actually inflicting\nreturn: Whether"
        " or not the status could be inflicted",
    )

    TryInflictInfatuatedStatus = Symbol(
        [0x35F6C],
        [0x23121AC],
        None,
        "Inflicts the Infatuated status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    TryInflictBurnStatus = Symbol(
        [0x360F8],
        [0x2312338],
        None,
        "Inflicts the Burn status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to apply some"
        " special effect alongside the burn?\nr3: flag to log a message on"
        " failure\nstack[0]: flag to only perform the check for inflicting without"
        " actually inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictBurnStatusWholeTeam = Symbol(
        [0x363D8],
        [0x2312618],
        None,
        "Inflicts the Burn status condition on all team members if possible.\n\nNo"
        " params.",
    )

    TryInflictPoisonedStatus = Symbol(
        [0x36424],
        [0x2312664],
        None,
        "Inflicts the Poisoned status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictBadlyPoisonedStatus = Symbol(
        [0x366FC],
        [0x231293C],
        None,
        "Inflicts the Badly Poisoned status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    TryInflictFrozenStatus = Symbol(
        [0x369B8],
        [0x2312BF8],
        None,
        "Inflicts the Frozen status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure",
    )

    TryInflictConstrictionStatus = Symbol(
        [0x36BE0],
        [0x2312E20],
        None,
        "Inflicts the Constriction status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2:"
        " animation ID\nr3: flag to log a message on failure",
    )

    TryInflictShadowHoldStatus = Symbol(
        [0x36D38],
        [0x2312F78],
        None,
        "Inflicts the Shadow Hold (AKA Immobilized) status condition on a target"
        " monster if possible.\n\nr0: user entity pointer\nr1: target entity"
        " pointer\nr2: flag to log a message on failure",
    )

    TryInflictIngrainStatus = Symbol(
        [0x36EF0],
        [0x2313130],
        None,
        "Inflicts the Ingrain status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer",
    )

    TryInflictWrappedStatus = Symbol(
        [0x36FB4],
        [0x23131F4],
        None,
        "Inflicts the Wrapped status condition on a target monster if possible.\n\nThis"
        " also gives the user the Wrap status (Wrapped around foe).\n\nr0: user entity"
        " pointer\nr1: target entity pointer",
    )

    FreeOtherWrappedMonsters = Symbol(
        [0x371B0],
        [0x23133F0],
        None,
        "Frees from the wrap status all monsters which are wrapped by/around the"
        " monster passed as parameter.\n\nr0: pointer to entity",
    )

    TryInflictPetrifiedStatus = Symbol(
        [0x3722C],
        [0x231346C],
        None,
        "Inflicts the Petrified status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    LowerOffensiveStat = Symbol(
        [0x373BC],
        [0x23135FC],
        None,
        "Lowers the specified offensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of"
        " stages\nstack[0]: ?\nstack[1]: ?",
    )

    LowerDefensiveStat = Symbol(
        [0x375D4],
        [0x2313814],
        None,
        "Lowers the specified defensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of"
        " stages\nstack[0]: ?\nstack[1]: ?",
    )

    BoostOffensiveStat = Symbol(
        [0x3775C],
        [0x231399C],
        None,
        "Boosts the specified offensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of stages",
    )

    BoostDefensiveStat = Symbol(
        [0x378C8],
        [0x2313B08],
        None,
        "Boosts the specified defensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of stages",
    )

    ApplyOffensiveStatMultiplier = Symbol(
        [0x37B00],
        [0x2313D40],
        None,
        "Applies a multiplier to the specified offensive stat on the target"
        " monster.\n\nThis affects struct"
        " monster_stat_modifiers::offensive_multipliers, for moves like Charm and"
        " Memento.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: stat"
        " index\nr3: multiplier\nstack[0]: ?",
    )

    ApplyDefensiveStatMultiplier = Symbol(
        [0x37D24],
        [0x2313F64],
        None,
        "Applies a multiplier to the specified defensive stat on the target"
        " monster.\n\nThis affects struct"
        " monster_stat_modifiers::defensive_multipliers, for moves like Screech.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: stat index\nr3:"
        " multiplier\nstack[0]: ?",
    )

    BoostHitChanceStat = Symbol(
        [0x37EA4],
        [0x23140E4],
        None,
        "Boosts the specified hit chance stat (accuracy or evasion) on the target"
        " monster.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: stat"
        " index",
    )

    LowerHitChanceStat = Symbol(
        [0x37FEC],
        [0x231422C],
        None,
        "Lowers the specified hit chance stat (accuracy or evasion) on the target"
        " monster.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: stat"
        " index\nr3: ?",
    )

    TryInflictCringeStatus = Symbol(
        [0x381A8],
        [0x23143E8],
        None,
        "Inflicts the Cringe status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictParalysisStatus = Symbol(
        [0x38304],
        [0x2314544],
        None,
        "Inflicts the Paralysis status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    BoostSpeed = Symbol(
        [0x385D0],
        [0x2314810],
        None,
        "Boosts the speed of the target monster.\n\nIf the number of turns specified is"
        " 0, a random turn count will be selected using the default"
        " SPEED_BOOST_DURATION_RANGE.\n\nr0: user entity pointer\nr1: target entity"
        " pointer\nr2: number of stages\nr3: number of turns\nstack[0]: flag to log a"
        " message on failure",
    )

    BoostSpeedOneStage = Symbol(
        [0x386FC],
        [0x231493C],
        None,
        "A wrapper around BoostSpeed with the number of stages set to 1.\n\nr0: user"
        " entity pointer\nr1: target entity pointer\nr2: number of turns\nr3: flag to"
        " log a message on failure",
    )

    LowerSpeed = Symbol(
        [0x38714],
        [0x2314954],
        None,
        "Lowers the speed of the target monster.\n\nr0: user entity pointer\nr1: target"
        " entity pointer\nr2: number of stages\nr3: flag to log a message on failure",
    )

    TrySealMove = Symbol(
        [0x3887C],
        [0x2314ABC],
        None,
        "Seals one of the target monster's moves. The move to be sealed is randomly"
        " selected.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nreturn: Whether or not a move was sealed",
    )

    BoostOrLowerSpeed = Symbol(
        [0x389EC],
        [0x2314C2C],
        None,
        "Randomly boosts or lowers the speed of the target monster by one stage with"
        " equal probability.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    ResetHitChanceStat = Symbol(
        [0x38A4C],
        [0x2314C8C],
        None,
        "Resets the specified hit chance stat (accuracy or evasion) back to normal on"
        " the target monster.\n\nr0: user entity pointer\nr1: target entity"
        " pointer\nr2: stat index\nr3: ?",
    )

    TryActivateQuickFeet = Symbol(
        [0x38BDC],
        [0x2314E1C],
        None,
        "Activate the Quick Feet ability on the defender, if the monster has it and"
        " it's active.\n\nr0: attacker pointer\nr1: defender pointer\nreturn: bool,"
        " whether or not the ability was activated",
    )

    TryInflictConfusedStatus = Symbol(
        [0x38CF8],
        [0x2314F38],
        None,
        "Inflicts the Confused status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictCoweringStatus = Symbol(
        [0x38F2C],
        [0x231516C],
        None,
        "Inflicts the Cowering status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryIncreaseHp = Symbol(
        [0x390A4],
        [0x23152E4],
        None,
        "Restore HP and possibly boost max HP of the target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: HP to restore\nr3: max HP"
        " boost\nstack[0]: flag to log a message on failure\nreturn: Success flag",
    )

    TryInflictLeechSeedStatus = Symbol(
        [0x395AC],
        [0x23157EC],
        None,
        "Inflicts the Leech Seed status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    TryInflictDestinyBond = Symbol(
        [0x39810],
        [0x2315A50],
        None,
        "Inflicts the Destiny Bond status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    IsBlinded = Symbol(
        [0x3B5A4],
        [0x23177E4],
        None,
        "Returns true if the monster has the blinded status (see statuses::blinded), or"
        " if it is not the leader and is holding Y-Ray Specs.\n\nr0: pointer to"
        " entity\nr1: flag for whether to check for the held item\nreturn: bool",
    )

    RestoreMovePP = Symbol(
        [0x3B9E0],
        [0x2317C20],
        None,
        "Restores the PP of all the target's moves by the specified amount.\n\nr0: user"
        " entity pointer\nr1: target entity pointer\nr2: PP to restore\nr3: flag to"
        " suppress message logging",
    )

    SetReflectDamageCountdownTo4 = Symbol(
        [0x3C180],
        [0x23183C0],
        None,
        "Sets the monster's reflect damage countdown to a global value (0x4).\n\nr0:"
        " pointer to entity",
    )

    HasConditionalGroundImmunity = Symbol(
        [0x3C80C],
        [0x2318A4C],
        None,
        "Checks if a monster is currently immune to Ground-type moves for reasons other"
        " than typing and ability.\n\nThis includes checks for Gravity and Magnet"
        " Rise.\n\nr0: entity pointer\nreturn: bool",
    )

    Conversion2IsActive = Symbol(
        [0x3D5D4],
        [0x2319814],
        None,
        "Checks if the monster is under the effect of Conversion 2 (its type was"
        " changed).\n\nReturns 1 if the effects is a status, 2 if it comes from an"
        " exclusive item, 0 otherwise.\n\nr0: pointer to entity\nreturn: int",
    )

    AiConsiderMove = Symbol(
        [0x3D640],
        [0x2319880],
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
        [0x3DD70],
        [0x2319FB0],
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
        [0x3DE64],
        [0x231A0A4],
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
        [0x3E454],
        [0x231A694],
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
        [0x3EA6C],
        [0x231ACAC],
        None,
        "Gets the move target-and-range field when used by a given entity. See struct"
        " move_target_and_range in the C headers.\n\nr0: entity pointer\nr1: move"
        " pointer\nr2: AI flag (same as GetMoveTargetAndRange)\nreturn: move target and"
        " range",
    )

    ApplyItemEffect = Symbol(
        [0x3F44C],
        [0x231B68C],
        None,
        "Seems to apply an item's effect via a giant switch statement?\n\nr3: attacker"
        " pointer\nstack[0]: defender pointer\nstack[1]: thrown item"
        " pointer\nothers: ?",
    )

    ViolentSeedBoost = Symbol(
        [0x40BDC],
        [0x231CE1C],
        None,
        "Applies the Violent Seed boost to an entity.\n\nr0: attacker pointer\nr1:"
        " defender pointer",
    )

    ApplyGummiBoostsDungeonMode = Symbol(
        [0x40E80],
        [0x231D0C0],
        None,
        "Applies the IQ and possible stat boosts from eating a Gummi to the target"
        " monster.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: Gummi"
        " type ID\nr3: Stat boost amount, if a random stat boost occurs",
    )

    GetMaxPpWrapper = Symbol(
        [0x427B0],
        [0x231E9F0],
        None,
        "Gets the maximum PP for a given move. A wrapper around the function in the ARM"
        " 9 binary.\n\nr0: move pointer\nreturn: max PP for the given move, capped"
        " at 99",
    )

    MoveIsNotPhysical = Symbol(
        [0x427D8],
        [0x231EA18],
        None,
        "Checks if a move isn't a physical move.\n\nr0: move ID\nreturn: bool",
    )

    TryPounce = Symbol(
        [0x439E0],
        [0x231FC20],
        None,
        "Makes the target monster execute the Pounce action in a given direction if"
        " possible.\n\nIf the direction ID is 8, the target will pounce in the"
        " direction it's currently facing.\n\nr0: user entity pointer\nr1: target"
        " entity pointer\nr2: direction ID",
    )

    TryBlowAway = Symbol(
        [0x43BA0],
        [0x231FDE0],
        None,
        "Blows away the target monster in a given direction if possible.\n\nr0: user"
        " entity pointer\nr1: target entity pointer\nr2: direction ID",
    )

    TryWarp = Symbol(
        [0x44AC8],
        [0x2320D08],
        None,
        "Makes the target monster warp if possible.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: warp type\nr3: position (if warp type is"
        " position-based)",
    )

    MoveHitCheck = Symbol(
        [0x47A08],
        [0x2323C48],
        None,
        "Determines if a move used hits or misses the target. It gets called twice per"
        " target, once with r3 = false and a second time with r3 = true.\n\nr0:"
        " Attacker\nr1: Defender\nr2: Pointer to move data\nr3: True if the move's"
        " first accuracy (accuracy1) should be used, false if its second accuracy"
        " (accuracy2) should be used instead.\nreturns: True if the move hits, false if"
        " it misses.",
    )

    DungeonRandOutcomeUserTargetInteraction = Symbol(
        [0x486F4],
        [0x2324934],
        None,
        "Like DungeonRandOutcome, but specifically for user-target"
        " interactions.\n\nThis modifies the underlying random process depending on"
        " factors like Serene Grace, and whether or not either entity has"
        " fainted.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: base"
        " success percentage (100*p). 0 is treated specially and guarantees success.",
    )

    DungeonRandOutcomeUserAction = Symbol(
        [0x487E0],
        [0x2324A20],
        None,
        "Like DungeonRandOutcome, but specifically for user actions.\n\nThis modifies"
        " the underlying random process to factor in Serene Grace (and checks whether"
        " the user is a valid entity).\n\nr0: entity pointer\nr1: base success"
        " percentage (100*p). 0 is treated specially and guarantees success.",
    )

    CanAiUseMove = Symbol(
        [0x48834],
        [0x2324A74],
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
        [0x488E4],
        [0x2324B24],
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
        [0x48B4C],
        [0x2324D8C],
        None,
        "Updates the PP of any moves that were used by a monster, if PP should be"
        " consumed.\n\nr0: entity pointer\nr1: flag for whether or not PP should be"
        " consumed",
    )

    LowerSshort = Symbol(
        [0x48C24],
        [0x2324E64],
        None,
        "Gets the lower 2 bytes of a 4-byte number and interprets it as a signed"
        " short.\n\nr0: 4-byte number x\nreturn: (short) x",
    )

    GetMoveAnimationId = Symbol(
        [0x498D0],
        [0x2325B10],
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
        [0x49A38],
        [0x2325C78],
        None,
        "Checks whether a moved used by a monster should play its alternative"
        " animation. Includes checks for Curse, Snore, Sleep Talk, Solar Beam and"
        " 2-turn moves.\n\nr0: Pointer to the entity that used the move\nr1: Move"
        " pointer\nreturn: True if the move should play its alternative animation",
    )

    DealDamageWithRecoil = Symbol(
        [0x4BCF4],
        [0x2327F34],
        None,
        "Deals damage from a move or item used by an attacking monster on a defending"
        " monster, and also deals recoil damage to the attacker.\n\nr0: attacker"
        " pointer\nr1: defender pointer\nr2: move\nr3: item ID\nreturn: bool, whether"
        " or not damage was dealt",
    )

    ExecuteMoveEffect = Symbol(
        [0x52624],
        [0x232E864],
        None,
        "Handles the effects that happen after a move is used. Includes a loop that is"
        " run for each target, mutiple ability checks and the giant switch statement"
        " that executes the effect of the move used given its ID.\n\nr0: pointer to"
        " some struct\nr1: attacker pointer\nr2: pointer to move data\nr3:"
        " ?\nstack[0]: ?",
    )

    DealDamage = Symbol(
        [0x568E0],
        [0x2332B20],
        None,
        "Deals damage from a move or item used by an attacking monster on a defending"
        " monster.\n\nr0: attacker pointer\nr1: defender pointer\nr2: move\nr3: damage"
        " multiplier (as a binary fixed-point number with 8 fraction bits)\nstack[0]:"
        " item ID\nreturn: amount of damage dealt",
    )

    CalcDamageProjectile = Symbol(
        [0x56A0C],
        [0x2332C4C],
        None,
        "Appears to calculate damage from a variable-damage projectile.\n\nr0: entity"
        " pointer 1?\nr1: entity pointer 2?\nr2: move pointer\nr3: move"
        " power\nothers: ?",
    )

    CalcDamageFinal = Symbol(
        [0x56B2C],
        [0x2332D6C],
        None,
        "Last function called by DealDamage to determine the final damage dealt by the"
        " move. The result of this call is the return value of DealDamage. \n\nr0:"
        " Attacker pointer\nr1: Defender pointer\nr2: Move pointer\nr3: ?\nstack[0]:"
        " Pointer to some struct. The first byte contains the ID of the move used.",
    )

    StatusCheckerCheck = Symbol(
        [0x56E34],
        [0x2333074],
        None,
        "Determines if using a given move against its intended targets would be"
        " redundant because all of them already have the effect caused by said"
        " move.\n\nr0: Pointer to the entity that is considering using the move\nr1:"
        " Move pointer\nreturn: True if it makes sense to use the move, false if it"
        " would be redundant given the effects it causes and the effects that all the"
        " targets already have.",
    )

    GetApparentWeather = Symbol(
        [0x58AC8],
        [0x2334D08],
        None,
        "Get the weather, as experienced by a specific entity.\n\nr0: entity"
        " pointer\nreturn: weather ID",
    )

    TryWeatherFormChange = Symbol(
        [0x58F30],
        [0x2335170],
        None,
        "Tries to change a monster into one of its weather-related alternative forms."
        " Applies to Castform and Cherrim, and checks for their unique"
        " abilities.\n\nr0: pointer to entity",
    )

    GetTile = Symbol(
        [0x59EBC],
        [0x23360FC],
        None,
        "Get the tile at some position. If the coordinates are out of bounds, returns a"
        " default tile.\n\nr0: x position\nr1: y position\nreturn: tile pointer",
    )

    GetTileSafe = Symbol(
        [0x59F24],
        [0x2336164],
        None,
        "Get the tile at some position. If the coordinates are out of bounds, returns a"
        " pointer to a copy of the default tile.\n\nr0: x position\nr1: y"
        " position\nreturn: tile pointer",
    )

    GetStairsRoom = Symbol(
        [0x5A1E8],
        [0x2336428],
        None,
        "Returns the index of the room that contains the stairs\n\nreturn: Room index",
    )

    GravityIsActive = Symbol(
        [0x5C150],
        [0x2338390],
        None,
        "Checks if gravity is active on the floor.\n\nreturn: bool",
    )

    IsSecretBazaar = Symbol(
        [0x5C384],
        [0x23385C4],
        None,
        "Checks if the current floor is the Secret Bazaar.\n\nreturn: bool",
    )

    IsSecretRoom = Symbol(
        [0x5C41C],
        [0x233865C],
        None,
        "Checks if the current floor is the Secret Room fixed floor (from hidden"
        " stairs).\n\nreturn: bool",
    )

    IsSecretFloor = Symbol(
        [0x5C444],
        [0x2338684],
        None,
        "Checks if the current floor is a secret bazaar or a secret room.\n\nreturn:"
        " bool",
    )

    GetDungeonGenInfoUnk0C = Symbol(
        [0x5C640], [0x2338880], None, "return: dungeon_generation_info::field_0xc"
    )

    GetMinimapData = Symbol(
        [0x5CED8],
        [0x2339118],
        None,
        "Returns a pointer to the minimap_display_data struct in the dungeon"
        " struct.\n\nreturn: minimap_display_data*",
    )

    SetMinimapDataE447 = Symbol(
        [0x5DFD8],
        [0x233A218],
        None,
        "Sets minimap_display_data::field_0xE447 to the specified value\n\nr0: Value to"
        " set the field to",
    )

    GetMinimapDataE447 = Symbol(
        None,
        None,
        None,
        "Exclusive to the EU ROM. Returns"
        " minimap_display_data::field_0xE447.\n\nreturn:"
        " minimap_display_data::field_0xE447",
    )

    SetMinimapDataE448 = Symbol(
        [0x5DFF0],
        [0x233A230],
        None,
        "Sets minimap_display_data::field_0xE448 to the specified value\n\nr0: Value to"
        " set the field to",
    )

    LoadFixedRoomDataVeneer = Symbol(
        [0x5E3E4],
        [0x233A624],
        None,
        "Likely a linker-generated veneer for LoadFixedRoomData.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nNo"
        " params.",
    )

    IsNormalFloor = Symbol(
        [0x5E414],
        [0x233A654],
        None,
        "Checks if the current floor is a normal layout.\n\n'Normal' means any layout"
        " that is NOT one of the following:\n- Hidden stairs floors\n- Golden"
        " Chamber\n- Challenge Request floor\n- Outlaw hideout\n- Treasure Memo"
        " floor\n- Full-room fixed floors (ID < 0xA5) [0xA5 == Sealed"
        " Chamber]\n\nreturn: bool",
    )

    GenerateFloor = Symbol(
        [0x5E498],
        [0x233A6D8],
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
        [0x5EC38],
        [0x233AE78],
        None,
        "Gets the terrain type of a tile.\n\nr0: tile pointer\nreturn: terrain ID",
    )

    DungeonRand100 = Symbol(
        [0x5EC44],
        [0x233AE84],
        None,
        "Compute a pseudorandom integer on the interval [0, 100) using the dungeon"
        " PRNG.\n\nreturn: pseudorandom integer",
    )

    FlagHallwayJunctions = Symbol(
        [0x5ECCC],
        [0x233AF0C],
        None,
        "Sets the junction flag (bit 3 of the terrain flags) on any hallway junction"
        " tiles in some range [x0, x1), [y0, y1). This leaves tiles within rooms"
        " untouched.\n\nA hallway tile is considered a junction if it has at least 3"
        " cardinal neighbors with open terrain.\n\nr0: x0\nr1: y0\nr2: x1\nr3: y1",
    )

    GenerateStandardFloor = Symbol(
        [0x5EDE8],
        [0x233B028],
        None,
        "Generate a standard floor with the given parameters.\n\nBroadly speaking, a"
        " standard floor is generated as follows:\n1. Generating the grid\n2. Creating"
        " a room or hallway anchor in each grid cell\n3. Creating hallways between grid"
        " cells\n4. Generating special features (maze room, Kecleon shop, Monster"
        " House, extra hallways, room imperfections, secondary structures)\n\nr0: grid"
        " size x\nr1: grid size y\nr2: floor properties",
    )

    GenerateOuterRingFloor = Symbol(
        [0x5EF50],
        [0x233B190],
        None,
        "Generates a floor layout with a 4x2 grid of rooms, surrounded by an outer ring"
        " of hallways.\n\nr0: floor properties",
    )

    GenerateCrossroadsFloor = Symbol(
        [0x5F3DC],
        [0x233B61C],
        None,
        "Generates a floor layout with a mesh of hallways on the interior 3x2 grid,"
        " surrounded by a boundary of rooms protruding from the interior like spikes,"
        " excluding the corner cells.\n\nr0: floor properties",
    )

    GenerateLineFloor = Symbol(
        [0x5F83C],
        [0x233BA7C],
        None,
        "Generates a floor layout with 5 grid cells in a horizontal line.\n\nr0: floor"
        " properties",
    )

    GenerateCrossFloor = Symbol(
        [0x5F99C],
        [0x233BBDC],
        None,
        "Generates a floor layout with 5 rooms arranged in a cross ('plus sign')"
        " formation.\n\nr0: floor properties",
    )

    GenerateBeetleFloor = Symbol(
        [0x5FB34],
        [0x233BD74],
        None,
        "Generates a floor layout in a 'beetle' formation, which is created by taking a"
        " 3x3 grid of rooms, connecting the rooms within each row, and merging the"
        " central column into one big room.\n\nr0: floor properties",
    )

    MergeRoomsVertically = Symbol(
        [0x5FCF0],
        [0x233BF30],
        None,
        "Merges two vertically stacked rooms into one larger room.\n\nr0: x grid"
        " coordinate of the rooms to merge\nr1: y grid coordinate of the upper"
        " room\nr2: dy, where the lower room has a y grid coordinate of y+dy\nr3: grid"
        " to update",
    )

    GenerateOuterRoomsFloor = Symbol(
        [0x5FE3C],
        [0x233C07C],
        None,
        "Generates a floor layout with a ring of rooms on the grid boundary and nothing"
        " in the interior.\n\nNote that this function is bugged, and won't properly"
        " connect all the rooms together for grid_size_x < 4.\n\nr0: grid size x\nr1:"
        " grid size y\nr2: floor properties",
    )

    IsNotFullFloorFixedRoom = Symbol(
        [0x600D0],
        [0x233C310],
        None,
        "Checks if a fixed room ID does not correspond to a fixed, full-floor"
        " layout.\n\nThe first non-full-floor fixed room is 0xA5, which is for Sealed"
        " Chambers.\n\nr0: fixed room ID\nreturn: bool",
    )

    GenerateFixedRoom = Symbol(
        [0x600EC],
        [0x233C32C],
        None,
        "Handles fixed room generation if the floor contains a fixed room.\n\nr0: fixed"
        " room ID\nr1: floor properties\nreturn: bool",
    )

    GenerateOneRoomMonsterHouseFloor = Symbol(
        [0x60534],
        [0x233C774],
        None,
        "Generates a floor layout with just a large, one-room Monster House.\n\nThis is"
        " the default layout if dungeon generation fails.\n\nNo params.",
    )

    GenerateTwoRoomsWithMonsterHouseFloor = Symbol(
        [0x60604],
        [0x233C844],
        None,
        "Generate a floor layout with two rooms (left and right), one of which is a"
        " Monster House.\n\nNo params.",
    )

    GenerateExtraHallways = Symbol(
        [0x607A8],
        [0x233C9E8],
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
        [0x60D44],
        [0x233CF84],
        None,
        "Get the grid cell positions for a given set of floor grid dimensions.\n\nr0:"
        " [output] pointer to array of the starting x coordinates of each grid"
        " column\nr1: [output] pointer to array of the starting y coordinates of each"
        " grid row\nr2: grid size x\nr3: grid size y",
    )

    InitDungeonGrid = Symbol(
        [0x60DC4],
        [0x233D004],
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
        [0x60EC4],
        [0x233D104],
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
        [0x610D8],
        [0x233D318],
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
        [0x61434],
        [0x233D674],
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
        [0x61E1C],
        [0x233E05C],
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
        [0x621FC],
        [0x233E43C],
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
        [0x62AF4],
        [0x233ED34],
        None,
        "Attempt to generate room imperfections for each room in the floor layout, if"
        " enabled.\n\nEach room has a 40% chance of having imperfections if its grid"
        " cell is flagged to allow room imperfections. Imperfections are generated by"
        " randomly growing the walls of the room inwards for a certain number of"
        " iterations, starting from the corners.\n\nr0: grid to update\nr1: grid size"
        " x\nr2: grid size y",
    )

    CreateHallway = Symbol(
        [0x62EE0],
        [0x233F120],
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
        [0x631E4],
        [0x233F424],
        None,
        "Ensure the grid forms a connected graph (all valid cells are reachable) by"
        " adding hallways to unreachable grid cells.\n\nIf a grid cell cannot be"
        " connected for some reason, remove it entirely.\n\nr0: grid to update\nr1:"
        " grid size x\nr2: grid size y\nr3: array of the starting x coordinates of each"
        " grid column\nstack[0]: array of the starting y coordinates of each grid row",
    )

    SetTerrainObstacleChecked = Symbol(
        [0x636C0],
        [0x233F900],
        None,
        "Set the terrain of a specific tile to be an obstacle (wall or secondary"
        " terrain).\n\nSecondary terrain (water/lava) can only be placed in the"
        " specified room. If the tile room index does not match, a wall will be placed"
        " instead.\n\nr0: tile pointer\nr1: use secondary terrain flag (true for"
        " water/lava, false for wall)\nr2: room index",
    )

    FinalizeJunctions = Symbol(
        [0x636FC],
        [0x233F93C],
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
        [0x639A8],
        [0x233FBE8],
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
        [0x63D5C],
        [0x233FF9C],
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
        [0x63FE4],
        [0x2340224],
        None,
        "Possibly generate a maze room on the floor.\n\nA maze room will be generated"
        " with a probability determined by the maze room chance parameter. A maze will"
        " be generated in a random room that is valid, connected, has odd dimensions,"
        " and has no other features.\n\nr0: grid to update\nr1: grid size x\nr2: grid"
        " size y\nr3: maze room chance (percentage from 0-100)",
    )

    GenerateMaze = Symbol(
        [0x64218],
        [0x2340458],
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
        [0x64494],
        [0x23406D4],
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
        [0x6463C],
        [0x234087C],
        None,
        "Set spawn flag 5 (0b100000 or 0x20) on all tiles in a room.\n\nr0: grid cell",
    )

    IsNextToHallway = Symbol(
        [0x64690],
        [0x23408D0],
        None,
        "Checks if a tile position is either in a hallway or next to one.\n\nr0: x\nr1:"
        " y\nreturn: bool",
    )

    ResolveInvalidSpawns = Symbol(
        [0x64734],
        [0x2340974],
        None,
        "Resolve invalid spawn flags on tiles.\n\nSpawn flags can be invalid due to"
        " terrain. For example, traps can't spawn on obstacles. Spawn flags can also be"
        " invalid due to multiple being set on a single tile, in which case one will"
        " take precedence. For example, stair spawns trump trap spawns.\n\nNo params.",
    )

    ConvertSecondaryTerrainToChasms = Symbol(
        [0x647CC],
        [0x2340A0C],
        None,
        "Converts all secondary terrain tiles (water/lava) to chasms.\n\nNo params.",
    )

    EnsureImpassableTilesAreWalls = Symbol(
        [0x64838],
        [0x2340A78],
        None,
        "Ensures all tiles with the impassable flag are walls.\n\nNo params.",
    )

    InitializeTile = Symbol(
        [0x64894], [0x2340AD4], None, "Initialize a tile struct.\n\nr0: tile pointer"
    )

    ResetFloor = Symbol(
        [0x648CC],
        [0x2340B0C],
        None,
        "Resets the floor in preparation for a floor generation attempt.\n\nResets all"
        " tiles, resets the border to be impassable, and clears entity spawns.\n\nNo"
        " params.",
    )

    PosIsOutOfBounds = Symbol(
        [0x64A6C],
        [0x2340CAC],
        None,
        "Checks if a position (x, y) is out of bounds on the map: !((0 <= x <= 55) &&"
        " (0 <= y <= 31)).\n\nr0: x\nr1: y\nreturn: bool",
    )

    ShuffleSpawnPositions = Symbol(
        [0x64AA4],
        [0x2340CE4],
        None,
        "Randomly shuffle an array of spawn positions.\n\nr0: spawn position array"
        " containing bytes {x1, y1, x2, y2, ...}\nr1: number of (x, y) pairs in the"
        " spawn position array",
    )

    SpawnNonEnemies = Symbol(
        [0x64B0C],
        [0x2340D4C],
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
        [0x65230],
        [0x2341470],
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
        [0x6552C],
        [0x234176C],
        None,
        "Set a specific tile to have secondary terrain (water/lava), but only if it's a"
        " passable wall.\n\nr0: tile pointer",
    )

    GenerateSecondaryTerrainFormations = Symbol(
        [0x6556C],
        [0x23417AC],
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
        [0x65C2C],
        [0x2341E6C],
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
        [0x66308], [0x2342548], None, "Converts all wall tiles to chasms.\n\nNo params."
    )

    ResetInnerBoundaryTileRows = Symbol(
        [0x6693C],
        [0x2342B7C],
        None,
        "Reset the inner boundary tile rows (y == 1 and y == 30) to their initial state"
        " of all wall tiles, with impassable walls at the edges (x == 0 and x =="
        " 55).\n\nNo params.",
    )

    SpawnStairs = Symbol(
        [0x66A4C],
        [0x2342C8C],
        None,
        "Spawn stairs at the given location.\n\nIf the hidden stairs flag is set,"
        " hidden stairs will be spawned instead of normal stairs.\n\nIf spawning normal"
        " stairs and the current floor is a rescue floor, the room containing the"
        " stairs will be converted into a Monster House.\n\nr0: position (two-byte"
        " array for {x, y})\nr1: dungeon generation info pointer (a field on the"
        " dungeon struct)\nr2: hidden stairs flag",
    )

    LoadFixedRoomData = Symbol(
        [0x67B50],
        [0x2343D90],
        None,
        "Loads fixed room data from BALANCE/fixed.bin into the buffer pointed to by"
        " FIXED_ROOM_DATA_PTR.\n\nNo params.",
    )

    IsHiddenStairsFloor = Symbol(
        [0x682CC],
        [0x234450C],
        None,
        "Checks if the current floor is either the Secret Bazaar or a Secret"
        " Room.\n\nreturn: bool",
    )

    HasHeldItem = Symbol(
        [0x6A5A4],
        [0x23467E4],
        None,
        "Checks if a monster has a certain held item.\n\nr0: entity pointer\nr1: item"
        " ID\nreturn: bool",
    )

    IsOutlawOrChallengeRequestFloor = Symbol(
        [0x6CF84],
        [0x23491C4],
        None,
        "Checks if the current floor is an active mission destination of type"
        " MISSION_TAKE_ITEM_FROM_OUTLAW, MISSION_ARREST_OUTLAW or"
        " MISSION_CHALLENGE_REQUEST.\n\nreturn: bool",
    )

    IsCurrentMissionType = Symbol(
        [0x6CFDC],
        [0x234921C],
        None,
        "Checks if the current floor is an active mission destination of a given type"
        " (and any subtype).\n\nr0: mission type\nreturn: bool",
    )

    IsCurrentMissionTypeExact = Symbol(
        [0x6D010],
        [0x2349250],
        None,
        "Checks if the current floor is an active mission destination of a given type"
        " and subtype.\n\nr0: mission type\nr1: mission subtype\nreturn: bool",
    )

    IsOutlawMonsterHouseFloor = Symbol(
        [0x6D04C],
        [0x234928C],
        None,
        "Checks if the current floor is a mission destination for a Monster House"
        " outlaw mission.\n\nreturn: bool",
    )

    IsGoldenChamber = Symbol(
        [0x6D070],
        [0x23492B0],
        None,
        "Checks if the current floor is a Golden Chamber floor.\n\nreturn: bool",
    )

    IsLegendaryChallengeFloor = Symbol(
        [0x6D094],
        [0x23492D4],
        None,
        "Checks if the current floor is a boss floor for a Legendary Challenge Letter"
        " mission.\n\nreturn: bool",
    )

    IsJirachiChallengeFloor = Symbol(
        [0x6D0D4],
        [0x2349314],
        None,
        "Checks if the current floor is the boss floor in Star Cave Pit for Jirachi's"
        " Challenge Letter mission.\n\nreturn: bool",
    )

    IsDestinationFloorWithMonster = Symbol(
        [0x6D10C],
        [0x234934C],
        None,
        "Checks if the current floor is a mission destination floor with a special"
        " monster.\n\nSee FloorHasMissionMonster for details.\n\nreturn: bool",
    )

    LoadMissionMonsterSprites = Symbol(
        [0x6D1B8],
        [0x23493F8],
        None,
        "Loads the sprites of monsters that appear on the current floor because of a"
        " mission, if applicable.\n\nThis includes monsters to be rescued, outlaws and"
        " its minions.\n\nNo params.",
    )

    MissionTargetEnemyIsDefeated = Symbol(
        [0x6D230],
        [0x2349470],
        None,
        "Checks if the target enemy of the mission on the current floor has been"
        " defeated.\n\nreturn: bool",
    )

    SetMissionTargetEnemyDefeated = Symbol(
        [0x6D250],
        [0x2349490],
        None,
        "Set the flag for whether or not the target enemy of the current mission has"
        " been defeated.\n\nr0: new flag value",
    )

    IsDestinationFloorWithFixedRoom = Symbol(
        [0x6D264],
        [0x23494A4],
        None,
        "Checks if the current floor is a mission destination floor with a fixed"
        " room.\n\nThe entire floor can be a fixed room layout, or it can just contain"
        " a Sealed Chamber.\n\nreturn: bool",
    )

    GetItemToRetrieve = Symbol(
        [0x6D28C],
        [0x23494CC],
        None,
        "Get the ID of the item that needs to be retrieve on the current floor for a"
        " mission, if one exists.\n\nreturn: item ID",
    )

    GetItemToDeliver = Symbol(
        [0x6D2B0],
        [0x23494F0],
        None,
        "Get the ID of the item that needs to be delivered to a mission client on the"
        " current floor, if one exists.\n\nreturn: item ID",
    )

    GetSpecialTargetItem = Symbol(
        [0x6D2DC],
        [0x234951C],
        None,
        "Get the ID of the special target item for a Sealed Chamber or Treasure Memo"
        " mission on the current floor.\n\nreturn: item ID",
    )

    IsDestinationFloorWithItem = Symbol(
        [0x6D324],
        [0x2349564],
        None,
        "Checks if the current floor is a mission destination floor with a special"
        " item.\n\nThis excludes missions involving taking an item from an"
        " outlaw.\n\nreturn: bool",
    )

    IsDestinationFloorWithHiddenOutlaw = Symbol(
        [0x6D384],
        [0x23495C4],
        None,
        "Checks if the current floor is a mission destination floor with a 'hidden"
        " outlaw' that behaves like a normal enemy.\n\nreturn: bool",
    )

    IsDestinationFloorWithFleeingOutlaw = Symbol(
        [0x6D3A8],
        [0x23495E8],
        None,
        "Checks if the current floor is a mission destination floor with a 'fleeing"
        " outlaw' that runs away.\n\nreturn: bool",
    )

    GetMissionTargetEnemy = Symbol(
        [0x6D3E0],
        [0x2349620],
        None,
        "Get the monster ID of the target enemy to be defeated on the current floor for"
        " a mission, if one exists.\n\nreturn: monster ID",
    )

    GetMissionEnemyMinionGroup = Symbol(
        [0x6D3F8],
        [0x2349638],
        None,
        "Get the monster ID of the specified minion group on the current floor for a"
        " mission, if it exists.\n\nNote that a single minion group can correspond to"
        " multiple actual minions of the same species. There can be up to 2 minion"
        " groups.\n\nr0: minion group index (0-indexed)\nreturn: monster ID",
    )

    SetTargetMonsterNotFoundFlag = Symbol(
        [0x6D484],
        [0x23496C4],
        None,
        "Sets dungeon::target_monster_not_found_flag to the specified value.\n\nr0:"
        " Value to set the flag to",
    )

    GetTargetMonsterNotFoundFlag = Symbol(
        [0x6D498],
        [0x23496D8],
        None,
        "Gets the value of dungeon::target_monster_not_found_flag.\n\nreturn:"
        " dungeon::target_monster_not_found_flag",
    )

    FloorHasMissionMonster = Symbol(
        [0x6D508],
        [0x2349748],
        None,
        "Checks if a given floor is a mission destination with a special monster,"
        " either a target to rescue or an enemy to defeat.\n\nMission types with a"
        " monster on the destination floor:\n- Rescue client\n- Rescue target\n- Escort"
        " to target\n- Deliver item\n- Search for target\n- Take item from outlaw\n-"
        " Arrest outlaw\n- Challenge Request\n\nr0: mission destination info"
        " pointer\nreturn: bool",
    )

    LogMessageByIdWithPopupCheckUser = Symbol(
        [0x6F064],
        [0x234B2A4],
        None,
        "Logs a message in the message log alongside a message popup, if the user"
        " hasn't fainted.\n\nr0: user entity pointer\nr1: message ID",
    )

    LogMessageWithPopupCheckUser = Symbol(
        [0x6F0A4],
        [0x234B2E4],
        None,
        "Logs a message in the message log alongside a message popup, if the user"
        " hasn't fainted.\n\nr0: user entity pointer\nr1: message string",
    )

    LogMessageByIdQuiet = Symbol(
        [0x6F0DC],
        [0x234B31C],
        None,
        "Logs a message in the message log (but without a message popup).\n\nr0: user"
        " entity pointer\nr1: message ID",
    )

    LogMessageQuiet = Symbol(
        [0x6F100],
        [0x234B340],
        None,
        "Logs a message in the message log (but without a message popup).\n\nr0: user"
        " entity pointer\nr1: message string",
    )

    LogMessageByIdWithPopupCheckUserTarget = Symbol(
        [0x6F110],
        [0x234B350],
        None,
        "Logs a message in the message log alongside a message popup, if some user"
        " check passes and the target hasn't fainted.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: message ID",
    )

    LogMessageWithPopupCheckUserTarget = Symbol(
        [0x6F164],
        [0x234B3A4],
        None,
        "Logs a message in the message log alongside a message popup, if some user"
        " check passes and the target hasn't fainted.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: message string",
    )

    LogMessageByIdQuietCheckUserTarget = Symbol(
        [0x6F1B0],
        [0x234B3F0],
        None,
        "Logs a message in the message log (but without a message popup), if some user"
        " check passes and the target hasn't fainted.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: message ID",
    )

    LogMessageByIdWithPopupCheckUserUnknown = Symbol(
        [0x6F204],
        [0x234B444],
        None,
        "Logs a message in the message log alongside a message popup, if the user"
        " hasn't fainted and some other unknown check.\n\nr0: user entity pointer\nr1:"
        " ?\nr2: message ID",
    )

    LogMessageByIdWithPopup = Symbol(
        [0x6F258],
        [0x234B498],
        None,
        "Logs a message in the message log alongside a message popup.\n\nr0: user"
        " entity pointer\nr1: message ID",
    )

    LogMessageWithPopup = Symbol(
        [0x6F27C],
        [0x234B4BC],
        None,
        "Logs a message in the message log alongside a message popup.\n\nr0: user"
        " entity pointer\nr1: message string",
    )

    LogMessage = Symbol(
        [0x6F2C8],
        [0x234B508],
        None,
        "Logs a message in the message log.\n\nr0: user entity pointer\nr1: message"
        " string\nr2: bool, whether or not to present a message popup",
    )

    LogMessageById = Symbol(
        [0x6F4D4],
        [0x234B714],
        None,
        "Logs a message in the message log.\n\nr0: user entity pointer\nr1: message"
        " ID\nr2: bool, whether or not to present a message popup",
    )

    OpenMessageLog = Symbol(
        [0x6F91C], [0x234BB5C], None, "Opens the message log window.\n\nr0: ?\nr1: ?"
    )

    RunDungeonMode = Symbol(
        [0x6FCE8],
        [0x234BF28],
        None,
        "This appears to be the top-level function for running dungeon mode.\n\nIt gets"
        " called by some code in overlay 10 right after doing the dungeon fade"
        " transition, and once it exits, the dungeon results are processed.\n\nThis"
        " function is presumably in charge of allocating the dungeon struct, setting it"
        " up, launching the dungeon engine, etc.",
    )

    DisplayDungeonTip = Symbol(
        [0x70CB0],
        [0x234CEF0],
        None,
        "Checks if a given dungeon tip should be displayed at the start of a floor and"
        " if so, displays it. Called up to 4 times at the start of each new floor, with"
        " a different r0 parameter each time.\n\nr0: Pointer to the message_tip struct"
        " of the message that should be displayed\nr1: True to log the message in the"
        " message log",
    )

    SetBothScreensWindowColorToDefault = Symbol(
        [0x70D20],
        [0x234CF60],
        None,
        "This changes the palettes of windows in both screens to an appropiate value"
        " depending on the playthrough\nIf you're in a special episode, they turn green"
        " , otherwise, they turn blue or pink depending on your character's sex\n\nNo"
        " params",
    )

    DisplayMessage = Symbol(
        [0x71018],
        [0x234D258],
        None,
        "Displays a message in a dialogue box that optionally waits for player input"
        " before closing.\n\nr0: ?\nr1: ID of the string to display\nr2: True to wait"
        " for player input before closing the dialogue box, false to close it"
        " automatically once all the characters get printed.",
    )

    DisplayMessage2 = Symbol(
        [0x7106C], [0x234D2AC], None, "Very similar to DisplayMessage"
    )

    DisplayMessageInternal = Symbol(
        [0x71350],
        [0x234D590],
        None,
        "Called by DisplayMessage. Seems to be the function that handles the display of"
        " the dialogue box. It won't return until all the characters have been written"
        " and after the player manually closes the dialogue box (if the corresponding"
        " parameter was set).\n\nr0: ID of the string to display\nr1: True to wait for"
        " player input before closing the dialogue box, false to close it automatically"
        " once all the characters get printed.\nr2: ? (r0 in DisplayMessage)\nr3:"
        " ?\nstack[0]: ?\nstack[1]: ?",
    )


class NaOverlay29Data:
    DUNGEON_STRUCT_SIZE = Symbol(
        [0x2838, 0x286C],
        [0x22DEA78, 0x22DEAAC],
        0x4,
        "Size of the dungeon struct (0x2CB14)",
    )

    MAX_HP_CAP = Symbol(
        [0x7B90, 0x355D4, 0x3C214],
        [0x22E3DD0, 0x2311814, 0x2318454],
        0x4,
        "The maximum amount of HP a monster can have (999).",
    )

    OFFSET_OF_DUNGEON_FLOOR_PROPERTIES = Symbol(
        [0xB7B8, 0x5EC28],
        [0x22E79F8, 0x233AE68],
        0x4,
        "Offset of the floor properties field in the dungeon struct (0x286B2)",
    )

    SPAWN_RAND_MAX = Symbol(
        [0xBC10],
        [0x22E7E50],
        0x4,
        "Equal to 10,000 (0x2710). Used as parameter for DungeonRandInt to generate the"
        " random number which determines the entity to spawn.",
    )

    DUNGEON_PRNG_LCG_MULTIPLIER = Symbol(
        [0xE788, 0xE84C],
        [0x22EA9C8, 0x22EAA8C],
        0x4,
        "The multiplier shared by all of the dungeon PRNG's LCGs, 1566083941"
        " (0x5D588B65).",
    )

    DUNGEON_PRNG_LCG_INCREMENT_SECONDARY = Symbol(
        [0xE854],
        [0x22EAA94],
        0x4,
        "The increment for the dungeon PRNG's secondary LCGs, 2531011 (0x269EC3). This"
        " happens to be the same increment that the Microsoft Visual C++ runtime"
        " library uses in its implementation of the rand() function.",
    )

    KECLEON_FEMALE_ID = Symbol(
        [0x1B1C4],
        [0x22F7404],
        0x4,
        "0x3D7 (983). Used when spawning Kecleon on an even numbered floor.",
    )

    KECLEON_MALE_ID = Symbol(
        [0x1B1C8],
        [0x22F7408],
        0x4,
        "0x17F (383). Used when spawning Kecleon on an odd numbered floor.",
    )

    MSG_ID_SLOW_START = Symbol(
        [0x1D090],
        [0x22F92D0],
        0x4,
        "ID of the message printed when a monster has the ability Slow Start at the"
        " beginning of the floor.",
    )

    EXPERIENCE_POINT_GAIN_CAP = Symbol(
        [0x26488],
        [0x23026C8],
        0x4,
        "A cap on the experience that can be given to a monster in one call to"
        " AddExpSpecial",
    )

    JUDGMENT_MOVE_ID = Symbol(
        [0x30218],
        [0x230C458],
        0x4,
        "Move ID for Judgment (0x1D3)\n\ntype: enum move_id",
    )

    REGULAR_ATTACK_MOVE_ID = Symbol(
        [0x3021C],
        [0x230C45C],
        0x4,
        "Move ID for the regular attack (0x163)\n\ntype: enum move_id",
    )

    DEOXYS_ATTACK_ID = Symbol(
        [0x30220],
        [0x230C460],
        0x4,
        "Monster ID for Deoxys in Attack Forme (0x1A3)\n\ntype: enum monster_id",
    )

    DEOXYS_SPEED_ID = Symbol(
        [0x30224],
        [0x230C464],
        0x4,
        "Monster ID for Deoxys in Speed Forme (0x1A5)\n\ntype: enum monster_id",
    )

    GIRATINA_ALTERED_ID = Symbol(
        [0x30228],
        [0x230C468],
        0x4,
        "Monster ID for Giratina in Altered Forme (0x211)\n\ntype: enum monster_id",
    )

    PUNISHMENT_MOVE_ID = Symbol(
        [0x3022C],
        [0x230C46C],
        0x4,
        "Move ID for Punishment (0x1BD)\n\ntype: enum move_id",
    )

    OFFENSE_STAT_MAX = Symbol(
        [0x3025C],
        [0x230C49C],
        0x4,
        "Cap on an attacker's modified offense (attack or special attack) stat after"
        " boosts. Used during damage calculation.",
    )

    PROJECTILE_MOVE_ID = Symbol(
        [0x30E3C, 0x404C0],
        [0x230D07C, 0x231C700],
        0x4,
        "The move ID of the special 'projectile' move (0x195)\n\ntype: enum move_id",
    )

    BELLY_LOST_PER_TURN = Symbol(
        [0x34830],
        [0x2310A70],
        0x4,
        "The base value by which belly is decreased every turn.\n\nIts raw value is"
        " 0x199A, which encodes a binary fixed-point number (16 fraction bits) with"
        " value (0x199A * 2^-16), and is the closest approximation to 0.1 representable"
        " in this number format.",
    )

    MOVE_TARGET_AND_RANGE_SPECIAL_USER_HEALING = Symbol(
        [0x3EAF4],
        [0x231AD34],
        0x4,
        "The move target and range code for special healing moves that target just the"
        " user (0x273).\n\ntype: struct move_target_and_range (+ padding)",
    )

    PLAIN_SEED_VALUE = Symbol(
        [0x40508], [0x231C748], 0x4, "Some value related to the Plain Seed (0xBE9)."
    )

    MAX_ELIXIR_PP_RESTORATION = Symbol(
        [0x4050C],
        [0x231C74C],
        0x4,
        "The amount of PP restored per move by ingesting a Max Elixir (0x3E7).",
    )

    SLIP_SEED_VALUE = Symbol(
        [0x4096C], [0x231CBAC], 0x4, "Some value related to the Slip Seed (0xC75)."
    )

    CASTFORM_NORMAL_FORM_MALE_ID = Symbol(
        [0x591F8], [0x2335438], 0x4, "Castform's male normal form ID (0x17B)"
    )

    CASTFORM_NORMAL_FORM_FEMALE_ID = Symbol(
        [0x591FC], [0x233543C], 0x4, "Castform's female normal form ID (0x3D3)"
    )

    CHERRIM_SUNSHINE_FORM_MALE_ID = Symbol(
        [0x59200], [0x2335440], 0x4, "Cherrim's male sunshine form ID (0x1CD)"
    )

    CHERRIM_OVERCAST_FORM_FEMALE_ID = Symbol(
        [0x59204], [0x2335444], 0x4, "Cherrim's female overcast form ID (0x424)"
    )

    CHERRIM_SUNSHINE_FORM_FEMALE_ID = Symbol(
        [0x59208], [0x2335448], 0x4, "Cherrim's female sunshine form ID (0x425)"
    )

    FLOOR_GENERATION_STATUS_PTR = Symbol(
        [
            0x5EC2C,
            0x5ECC8,
            0x5EF4C,
            0x5F3D8,
            0x5F838,
            0x5F998,
            0x5FB30,
            0x5FCEC,
            0x600CC,
            0x6052C,
            0x60D40,
            0x60EC0,
            0x610D0,
            0x61430,
            0x61E18,
            0x63D50,
            0x63FDC,
            0x64490,
            0x6521C,
            0x65524,
            0x65F38,
            0x662D0,
            0x665A0,
            0x66934,
            0x66A24,
            0x66B58,
            0x66CE8,
        ],
        [
            0x233AE6C,
            0x233AF08,
            0x233B18C,
            0x233B618,
            0x233BA78,
            0x233BBD8,
            0x233BD70,
            0x233BF2C,
            0x233C30C,
            0x233C76C,
            0x233CF80,
            0x233D100,
            0x233D310,
            0x233D670,
            0x233E058,
            0x233FF90,
            0x234021C,
            0x23406D0,
            0x234145C,
            0x2341764,
            0x2342178,
            0x2342510,
            0x23427E0,
            0x2342B74,
            0x2342C64,
            0x2342D98,
            0x2342F28,
        ],
        0x4,
        "Pointer to the global FLOOR_GENERATION_STATUS\n\ntype: struct"
        " floor_generation_status*",
    )

    OFFSET_OF_DUNGEON_N_NORMAL_ITEM_SPAWNS = Symbol(
        [0x5EC34, 0x65224],
        [0x233AE74, 0x2341464],
        0x4,
        "Offset of the (number of base items + 1) field on the dungeon struct"
        " (0x12AFA)",
    )

    DUNGEON_GRID_COLUMN_BYTES = Symbol(
        [
            0x5F3D4,
            0x5F834,
            0x5FB2C,
            0x5FCE8,
            0x600C8,
            0x60530,
            0x607A4,
            0x60D38,
            0x60EBC,
            0x610D4,
            0x6142C,
            0x61E14,
            0x621F8,
            0x62AF0,
            0x62ED4,
            0x636BC,
            0x63D54,
            0x63FE0,
            0x64214,
            0x6628C,
        ],
        [
            0x233B614,
            0x233BA74,
            0x233BD6C,
            0x233BF28,
            0x233C308,
            0x233C770,
            0x233C9E4,
            0x233CF78,
            0x233D0FC,
            0x233D314,
            0x233D66C,
            0x233E054,
            0x233E438,
            0x233ED30,
            0x233F114,
            0x233F8FC,
            0x233FF94,
            0x2340220,
            0x2340454,
            0x23424CC,
        ],
        0x4,
        "The number of bytes in one column of the dungeon grid cell array, 450, which"
        " corresponds to a column of 15 grid cells.",
    )

    DEFAULT_MAX_POSITION = Symbol(
        [0x63D58],
        [0x233FF98],
        0x4,
        "A large number (9999) to use as a default position for keeping track of"
        " min/max position values",
    )

    OFFSET_OF_DUNGEON_GUARANTEED_ITEM_ID = Symbol(
        [0x65220, 0x68C40],
        [0x2341460, 0x2344E80],
        0x4,
        "Offset of the guaranteed item ID field in the dungeon struct (0x2C9E8)",
    )

    FIXED_ROOM_TILE_SPAWN_TABLE = Symbol(
        [0x73B90],
        [0x234FDD0],
        0x2C,
        "Table of tiles that can spawn in fixed rooms, pointed into by the"
        " FIXED_ROOM_TILE_SPAWN_TABLE.\n\nThis is an array of 11 4-byte entries"
        " containing info about one tile each. Info includes the trap ID if a trap,"
        " room ID, and flags.\n\ntype: struct fixed_room_tile_spawn_entry[11]",
    )

    FIXED_ROOM_REVISIT_OVERRIDES = Symbol(
        [0x73BD4],
        [0x234FE14],
        0x100,
        "Table of fixed room IDs, which if nonzero, overrides the normal fixed room ID"
        " for a floor (which is used to index the table) if the dungeon has already"
        " been cleared previously.\n\nOverrides are used to substitute different fixed"
        " room data for things like revisits to story dungeons.\n\ntype: struct"
        " fixed_room_id_8[256]",
    )

    FIXED_ROOM_MONSTER_SPAWN_TABLE = Symbol(
        [0x73CD4],
        [0x234FF14],
        0x1E0,
        "Table of monsters that can spawn in fixed rooms, pointed into by the"
        " FIXED_ROOM_ENTITY_SPAWN_TABLE.\n\nThis is an array of 120 4-byte entries"
        " containing info about one monster each. Info includes the monster ID, stats,"
        " and behavior type.\n\ntype: struct fixed_room_monster_spawn_entry[120]",
    )

    FIXED_ROOM_ITEM_SPAWN_TABLE = Symbol(
        [0x73EB4],
        [0x23500F4],
        0x1F8,
        "Table of items that can spawn in fixed rooms, pointed into by the"
        " FIXED_ROOM_ENTITY_SPAWN_TABLE.\n\nThis is an array of 63 8-byte entries"
        " containing one item ID each.\n\ntype: struct fixed_room_item_spawn_entry[63]",
    )

    FIXED_ROOM_ENTITY_SPAWN_TABLE = Symbol(
        [0x740AC],
        [0x23502EC],
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
        [0x74F7C],
        [0x23511BC],
        0x10,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::muzzled * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_MAGNET_RISE = Symbol(
        [0x74F8C],
        [0x23511CC],
        0x10,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::magnet_rise * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_MIRACLE_EYE = Symbol(
        [0x74FAC],
        [0x23511EC],
        0x18,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::miracle_eye * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_LEECH_SEED = Symbol(
        [0x74FBC],
        [0x23511FC],
        0x18,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::leech_seed * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_LONG_TOSS = Symbol(
        [0x74FD4],
        [0x2351214],
        0x18,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::long_toss * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_BLINDED = Symbol(
        [0x7502C],
        [0x235126C],
        0x28,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::blinded * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_BURN = Symbol(
        [0x75054],
        [0x2351294],
        0x28,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::burn * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_SURE_SHOT = Symbol(
        [0x7507C],
        [0x23512BC],
        0x28,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::sure_shot * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_INVISIBLE = Symbol(
        [0x750A4],
        [0x23512E4],
        0x28,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::invisible * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_SLEEP = Symbol(
        [0x750CC],
        [0x235130C],
        0x40,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::sleep * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_CURSE = Symbol(
        [0x750FC],
        [0x235133C],
        0x38,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::curse * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_FREEZE = Symbol(
        [0x75034],
        [0x2351274],
        0x40,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::freeze * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_CRINGE = Symbol(
        [0x75174],
        [0x23513B4],
        0x40,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::cringe * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_BIDE = Symbol(
        [0x751B4],
        [0x23513F4],
        0x70,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::bide * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_REFLECT = Symbol(
        [0x752B4],
        [0x23514F4],
        0x90,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::reflect * 8. See UpdateStatusIconFlags for details.",
    )

    DIRECTIONS_XY = Symbol(
        [0x754DC],
        [0x235171C],
        0x20,
        "An array mapping each direction index to its x and y"
        " displacements.\n\nDirections start with 0=down and proceed counterclockwise"
        " (see enum direction_id). Displacements for x and y are interleaved and"
        " encoded as 2-byte signed integers. For example, the first two integers are"
        " [0, 1], which correspond to the x and y displacements for the 'down'"
        " direction (positive y means down).",
    )

    FRACTIONAL_TURN_SEQUENCE = Symbol(
        [0x76044],
        [0x2352284],
        0xFA,
        "Read by certain functions that are called by RunFractionalTurn to see if they"
        " should be executed.\n\nArray is accessed via a pointer added to some multiple"
        " of fractional_turn, so that if the resulting memory location is zero, the"
        " function returns.",
    )

    BELLY_DRAIN_IN_WALLS_INT = Symbol(
        [0x76528],
        [0x2352768],
        0x2,
        "The additional amount by which belly is decreased every turn when inside walls"
        " (integer part)",
    )

    BELLY_DRAIN_IN_WALLS_THOUSANDTHS = Symbol(
        [0x7652A],
        [0x235276A],
        0x2,
        "The additional amount by which belly is decreased every turn when inside walls"
        " (fractional thousandths)",
    )

    SPATK_STAT_IDX = Symbol(
        [0x768A8],
        [0x2352AE8],
        0x4,
        "The index (1) of the special attack entry in internal stat structs, such as"
        " the stat modifier array for a monster.",
    )

    ATK_STAT_IDX = Symbol(
        [0x768AC],
        [0x2352AEC],
        0x4,
        "The index (0) of the attack entry in internal stat structs, such as the stat"
        " modifier array for a monster.",
    )

    CORNER_CARDINAL_NEIGHBOR_IS_OPEN = Symbol(
        [0x76DD0],
        [0x2353010],
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
        [0x772F8],
        [0x2353538],
        0x4,
        "[Runtime] Pointer to the dungeon struct in dungeon mode.\n\nThis is a 'working"
        " copy' of DUNGEON_PTR_MASTER. The main dungeon engine uses this pointer (or"
        " rather pointers to this pointer) when actually running dungeon mode.\n\ntype:"
        " struct dungeon*",
    )

    DUNGEON_PTR_MASTER = Symbol(
        [0x772FC],
        [0x235353C],
        0x4,
        "[Runtime] Pointer to the dungeon struct in dungeon mode.\n\nThis is a 'master"
        " copy' of the dungeon pointer. The game uses this pointer when doing low-level"
        " memory work (allocation, freeing, zeroing). The normal DUNGEON_PTR is used"
        " for most other dungeon mode work.\n\ntype: struct dungeon*",
    )

    LEADER_PTR = Symbol(
        [0x7731C],
        [0x235355C],
        0x4,
        "[Runtime] Pointer to the current leader of the team.\n\ntype: struct entity*",
    )

    DUNGEON_PRNG_STATE = Symbol(
        [0x77330],
        [0x2353570],
        0x14,
        "[Runtime] The global PRNG state for dungeon mode, not including the current"
        " values in the secondary sequences.\n\nThis struct holds state for the primary"
        " LCG, as well as the current configuration controlling which LCG to use when"
        " generating random numbers. See DungeonRand16Bit for more information on how"
        " the dungeon PRNG works.\n\ntype: struct prng_state",
    )

    DUNGEON_PRNG_STATE_SECONDARY_VALUES = Symbol(
        [0x77344],
        [0x2353584],
        0x14,
        "[Runtime] An array of 5 integers corresponding to the last value generated for"
        " each secondary LCG sequence.\n\nBased on the assembly, this appears to be its"
        " own global array, separate from DUNGEON_PRNG_STATE.",
    )

    EXCL_ITEM_EFFECTS_WEATHER_ATK_SPEED_BOOST = Symbol(
        [0x77370],
        [0x23535B0],
        0x8,
        "Array of IDs for exclusive item effects that increase attack speed with"
        " certain weather conditions.",
    )

    EXCL_ITEM_EFFECTS_WEATHER_MOVE_SPEED_BOOST = Symbol(
        [0x77378],
        [0x23535B8],
        0x8,
        "Array of IDs for exclusive item effects that increase movement speed with"
        " certain weather conditions.",
    )

    EXCL_ITEM_EFFECTS_WEATHER_NO_STATUS = Symbol(
        [0x77380],
        [0x23535C0],
        0x8,
        "Array of IDs for exclusive item effects that grant status immunity with"
        " certain weather conditions.",
    )

    EXCL_ITEM_EFFECTS_EVASION_BOOST = Symbol(
        [0x774D0],
        [0x2353710],
        0x8,
        "Array of IDs for exclusive item effects that grant an evasion boost with"
        " certain weather conditions.",
    )

    DEFAULT_TILE = Symbol(
        [0x774E4],
        [0x2353724],
        0x14,
        "The default tile struct.\n\nThis is just a struct full of zeroes, but is used"
        " as a fallback in various places where a 'default' tile is needed, such as"
        " when a grid index is out of range.\n\ntype: struct tile",
    )

    FIXED_ROOM_DATA_PTR = Symbol(
        [0x77554],
        [0x2353794],
        0x4,
        "[Runtime] Pointer to decoded fixed room data loaded from the BALANCE/fixed.bin"
        " file.",
    )

    NECTAR_IQ_BOOST = Symbol(
        [0x40144], [0x231C384], None, "IQ boost from ingesting Nectar."
    )


class NaOverlay29Section:
    name = "overlay29"
    description = (
        "The dungeon engine.\n\nThis is the 'main' overlay of dungeon mode. It controls"
        " most things that happen in a Mystery Dungeon, such as dungeon layout"
        " generation, dungeon menus, enemy AI, and generally just running each turn"
        " while within a dungeon."
    )
    loadaddress = 0x22DC240
    length = 0x77620
    functions = NaOverlay29Functions
    data = NaOverlay29Data


class NaOverlay11Functions:
    FuncThatCallsCommandParsing = Symbol([0xF24], [0x22DD164], None, "")

    ScriptCommandParsing = Symbol([0x1B24], [0x22DDD64], None, "")

    SsbLoad2 = Symbol([0x84BC], [0x22E46FC], None, "")

    StationLoadHanger = Symbol([0x8994], [0x22E4BD4], None, "")

    ScriptStationLoadTalk = Symbol([0x91A4], [0x22E53E4], None, "")

    SsbLoad1 = Symbol([0x9B10], [0x22E5D50], None, "")

    ScriptSpecialProcessCall = Symbol(
        [0xAED8],
        [0x22E7118],
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
        [0x22E803C],
        None,
        "Returns an entry from RECRUITMENT_TABLE_SPECIES.\n\nNote: This indexes without"
        " doing bounds checking.\n\nr0: index into RECRUITMENT_TABLE_SPECIES\nreturn:"
        " enum monster_id",
    )

    PrepareMenuAcceptTeamMember = Symbol(
        [0xBE40],
        [0x22E8080],
        None,
        "Implements SPECIAL_PROC_PREPARE_MENU_ACCEPT_TEAM_MEMBER (see"
        " ScriptSpecialProcessCall).\n\nr0: index into RECRUITMENT_TABLE_SPECIES",
    )

    InitRandomNpcJobs = Symbol(
        [0xBEE4],
        [0x22E8124],
        None,
        "Implements SPECIAL_PROC_INIT_RANDOM_NPC_JOBS (see"
        " ScriptSpecialProcessCall).\n\nr0: job type? 0 is a random NPC job, 1 is a"
        " bottle mission\nr1: ?",
    )

    GetRandomNpcJobType = Symbol(
        [0xBF7C],
        [0x22E81BC],
        None,
        "Implements SPECIAL_PROC_GET_RANDOM_NPC_JOB_TYPE (see"
        " ScriptSpecialProcessCall).\n\nreturn: job type?",
    )

    GetRandomNpcJobSubtype = Symbol(
        [0xBF94],
        [0x22E81D4],
        None,
        "Implements SPECIAL_PROC_GET_RANDOM_NPC_JOB_SUBTYPE (see"
        " ScriptSpecialProcessCall).\n\nreturn: job subtype?",
    )

    GetRandomNpcJobStillAvailable = Symbol(
        [0xBFB0],
        [0x22E81F0],
        None,
        "Implements SPECIAL_PROC_GET_RANDOM_NPC_JOB_STILL_AVAILABLE (see"
        " ScriptSpecialProcessCall).\n\nreturn: bool",
    )

    AcceptRandomNpcJob = Symbol(
        [0xC018],
        [0x22E8258],
        None,
        "Implements SPECIAL_PROC_ACCEPT_RANDOM_NPC_JOB (see"
        " ScriptSpecialProcessCall).\n\nreturn: bool",
    )

    GroundMainLoop = Symbol(
        [0xC534],
        [0x22E8774],
        None,
        "Appears to be the main loop for ground mode.\n\nBased on debug print"
        " statements and general code structure, it seems contain a core loop, and"
        " dispatches to various functions in response to different events.\n\nr0: mode,"
        " which is stored globally and used in switch statements for dispatch\nreturn:"
        " return code",
    )

    GetAllocArenaGround = Symbol(
        [0xD11C],
        [0x22E935C],
        None,
        "The GetAllocArena function used for ground mode. See SetMemAllocatorParams for"
        " more information.\n\nr0: initial memory arena pointer, or null\nr1: flags"
        " (see MemAlloc)\nreturn: memory arena pointer, or null",
    )

    GetFreeArenaGround = Symbol(
        [0xD180],
        [0x22E93C0],
        None,
        "The GetFreeArena function used for ground mode. See SetMemAllocatorParams for"
        " more information.\n\nr0: initial memory arena pointer, or null\nr1: pointer"
        " to free\nreturn: memory arena pointer, or null",
    )

    GroundMainReturnDungeon = Symbol(
        [0xD1D4],
        [0x22E9414],
        None,
        "Implements SPECIAL_PROC_RETURN_DUNGEON (see ScriptSpecialProcessCall).\n\nNo"
        " params.",
    )

    GroundMainNextDay = Symbol(
        [0xD1F8],
        [0x22E9438],
        None,
        "Implements SPECIAL_PROC_NEXT_DAY (see ScriptSpecialProcessCall).\n\nNo"
        " params.",
    )

    JumpToTitleScreen = Symbol(
        [0xD39C],
        [0x22E95DC],
        None,
        "Implements SPECIAL_PROC_JUMP_TO_TITLE_SCREEN and SPECIAL_PROC_0x1A (see"
        " ScriptSpecialProcessCall).\n\nr0: int, argument value for"
        " SPECIAL_PROC_JUMP_TO_TITLE_SCREEN and -1 for SPECIAL_PROC_0x1A\nreturn: bool"
        " (but note that the special process ignores this and always returns 0)",
    )

    ReturnToTitleScreen = Symbol(
        [0xD454],
        [0x22E9694],
        None,
        "Implements SPECIAL_PROC_RETURN_TO_TITLE_SCREEN (see"
        " ScriptSpecialProcessCall).\n\nr0: fade duration\nreturn: bool (but note that"
        " the special process ignores this and always returns 0)",
    )

    ScriptSpecialProcess0x16 = Symbol(
        [0xD4B4],
        [0x22E96F4],
        None,
        "Implements SPECIAL_PROC_0x16 (see ScriptSpecialProcessCall).\n\nr0: bool",
    )

    SprintfStatic = Symbol(
        [0x2CC8C],
        [0x2308ECC],
        None,
        "Statically defined copy of sprintf(3) in overlay 11. See arm9.yml for more"
        " information.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )

    StatusUpdate = Symbol(
        [0x37858],
        [0x2313A98],
        None,
        "Implements SPECIAL_PROC_STATUS_UPDATE (see ScriptSpecialProcessCall).\n\nNo"
        " params.",
    )


class NaOverlay11Data:
    SCRIPT_OP_CODES = Symbol(
        [0x3C3D0],
        [0x2318610],
        0xBF8,
        "Table of opcodes for the script engine. There are 383 8-byte entries.\n\nThese"
        " opcodes underpin the various ExplorerScript functions you can call in the"
        " SkyTemple SSB debugger.\n\ntype: struct script_opcode_table",
    )

    C_ROUTINES = Symbol(
        [0x405E8],
        [0x231C828],
        0x15E8,
        "Common routines used within the unionall.ssb script (the master script). There"
        " are 701 8-byte entries.\n\nThese routines underpin the ExplorerScript"
        " coroutines you can call in the SkyTemple SSB debugger.\n\ntype: struct"
        " common_routine_table",
    )

    OBJECTS = Symbol(
        [0x42C14],
        [0x231EE54],
        0x1A04,
        "Table of objects for the script engine, which can be placed in scenes. There"
        " are a version-dependent number of 12-byte entries.\n\ntype: struct"
        " script_object[length / 12]",
    )

    RECRUITMENT_TABLE_LOCATIONS = Symbol(
        [0x44654],
        [0x2320894],
        0x16,
        "Table of dungeon IDs corresponding to entries in"
        " RECRUITMENT_TABLE_SPECIES.\n\ntype: struct dungeon_id_16[22]",
    )

    RECRUITMENT_TABLE_LEVELS = Symbol(
        [0x4466C],
        [0x23208AC],
        0x2C,
        "Table of levels for recruited Pokémon, corresponding to entries in"
        " RECRUITMENT_TABLE_SPECIES.\n\ntype: uint16_t[22]",
    )

    RECRUITMENT_TABLE_SPECIES = Symbol(
        [0x44698],
        [0x23208D8],
        0x2C,
        "Table of Pokémon recruited at special locations, such as at the ends of"
        " certain dungeons (e.g., Dialga or the Seven Treasures legendaries) or during"
        " a cutscene (e.g., Cresselia and Manaphy).\n\nInterestingly, this includes"
        " both Heatran genders. It also includes Darkrai for some reason?\n\ntype:"
        " struct monster_id_16[22]",
    )

    LEVEL_TILEMAP_LIST = Symbol([0x44AEC], [0x2320D2C], 0x288, "")

    OVERLAY11_OVERLAY_LOAD_TABLE = Symbol(
        [0x46E2C],
        [0x232306C],
        None,
        "The overlays that can be loaded while this one is loaded.\n\nEach entry is 16"
        " bytes, consisting of:\n- overlay group ID (see arm9.yml or enum"
        " overlay_group_id in the C headers for a mapping between group ID and overlay"
        " number)\n- function pointer to entry point\n- function pointer to"
        " destructor\n- possibly function pointer to frame-update function?",
    )

    UNIONALL_RAM_ADDRESS = Symbol([0x48A64], [0x2324CA4], None, "[Runtime]")

    GROUND_STATE_MAP = Symbol([0x48A80], [0x2324CC0], None, "[Runtime]")

    GROUND_STATE_PTRS = Symbol(
        [0x48AB4],
        [0x2324CF4],
        0x18,
        "Host pointers to multiple structure used for performing an overworld"
        " scene\n\ntype: struct main_ground_data",
    )


class NaOverlay11Section:
    name = "overlay11"
    description = (
        "The script engine.\n\nThis is the 'main' overlay of ground mode. The script"
        " engine is what runs the ground mode scripts contained in the SCRIPT folder,"
        " which are written in a custom scripting language. These scripts encode things"
        " like cutscenes, screen transitions, ground mode events, and tons of other"
        " things related to ground mode."
    )
    loadaddress = 0x22DC240
    length = 0x48C40
    functions = NaOverlay11Functions
    data = NaOverlay11Data


class NaOverlay25Functions:
    pass


class NaOverlay25Data:
    APPRAISAL_MENU_CONFIRM = Symbol([0x1374], [0x238B4B4], 0x18, "")

    APPRAISAL_MAIN_MENU = Symbol([0x138C], [0x238B4CC], 0x20, "")

    APPRAISAL_SUBMENU = Symbol([0x13AC], [0x238B4EC], 0x20, "")


class NaOverlay25Section:
    name = "overlay25"
    description = "Controls Xatu Appraisal."
    loadaddress = 0x238A140
    length = 0x14C0
    functions = NaOverlay25Functions
    data = NaOverlay25Data


class NaArm9Functions:
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
        [0xC110], [0x200C110], None, "Just returns 0 in the final binary."
    )

    SetDebugFlag1 = Symbol([0xC118], [0x200C118], None, "A no-op in the final binary.")

    AppendProgPos = Symbol(
        [0xC120],
        [0x200C120],
        None,
        "Write a base message into a string and append the file name and line number to"
        " the end in the format 'file = '%s'  line = %5d\n'.\n\nIf no program position"
        " info is given, 'ProgPos info NULL\n' is appended instead.\n\nr0: [output]"
        " str\nr1: program position info\nr2: base message\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )

    DebugPrintTrace = Symbol(
        [0xC16C],
        [0x200C16C],
        None,
        "Would log a printf format string tagged with the file name and line number in"
        " the debug binary.\n\nThis still constructs the string, but doesn't actually"
        " do anything with it in the final binary.\n\nIf message is a null pointer, the"
        " string '  Print  ' is used instead.\n\nr0: message\nr1: program position info"
        " (can be null)",
    )

    DebugPrint0 = Symbol(
        [0xC1C8, 0xC1FC],
        [0x200C1C8, 0x200C1FC],
        None,
        "Would log a printf format string in the debug binary.\n\nThis still constructs"
        " the string with Vsprintf, but doesn't actually do anything with it in the"
        " final binary.\n\nr0: format\n...: variadic",
    )

    GetDebugFlag2 = Symbol(
        [0xC234], [0x200C234], None, "Just returns 0 in the final binary."
    )

    SetDebugFlag2 = Symbol([0xC23C], [0x200C23C], None, "A no-op in the final binary.")

    DebugPrint = Symbol(
        [0xC240],
        [0x200C240],
        None,
        "Would log a printf format string in the debug binary. A no-op in the final"
        " binary.\n\nr0: log level\nr1: format\n...: variadic",
    )

    FatalError = Symbol(
        [0xC25C],
        [0x200C25C],
        None,
        "Logs some debug messages, then hangs the process.\n\nThis function is called"
        " in lots of places to bail on a fatal error. Looking at the static data"
        " callers use to fill in the program position info is informative, as it tells"
        " you the original file name (probably from the standard __FILE__ macro) and"
        " line number (probably from the standard __LINE__ macro) in the source"
        " code.\n\nr0: program position info\nr1: format\n...: variadic",
    )

    OpenAllPackFiles = Symbol(
        None,
        None,
        None,
        "Open the 6 files at PACK_FILE_PATHS_TABLE into PACK_FILE_OPENED. Called during"
        " game initialisation.\n\nNo params.",
    )

    GetFileLengthInPackWithPackNb = Symbol(
        None,
        None,
        None,
        "Call GetFileLengthInPack after looking up the global Pack archive by its"
        " number\n\nr0: pack file number\nr1: file number\nreturn: size of the file in"
        " bytes from the Pack Table of Content",
    )

    LoadFileInPackWithPackId = Symbol(
        None,
        None,
        None,
        "Call LoadFileInPack after looking up the global Pack archive by its"
        " identifier\n\nr0: pack file identifier\nr1: [output] target buffer\nr2: file"
        " index\nreturn: number of read bytes (identical to the length of the pack from"
        " the Table of Content)",
    )

    AllocAndLoadFileInPack = Symbol(
        None,
        None,
        None,
        "Allocate a file and load a file from the pack archive inside.\nThe data"
        " pointed by the pointer in the output need to be freed once is not needed"
        " anymore.\n\nr0: pack file identifier\nr1: file index\nr2: [output] result"
        " struct (will contain length and pointer)\nr3: allocation flags",
    )

    OpenPackFile = Symbol(
        None,
        None,
        None,
        "Open a Pack file, to be read later. Initialise the output structure.\n\nr0:"
        " [output] pack file struct\nr1: file name",
    )

    GetFileLengthInPack = Symbol(
        None,
        None,
        None,
        "Get the length of a file entry from a Pack archive\n\nr0: pack file"
        " struct\nr1: file index\nreturn: size of the file in bytes from the Pack Table"
        " of Content",
    )

    LoadFileInPack = Symbol(
        None,
        None,
        None,
        "Load the indexed file from the Pack archive, itself loaded from the"
        " ROM.\n\nr0: pack file struct\nr1: [output] target buffer\nr2: file"
        " index\nreturn: number of read bytes (identical to the length of the pack from"
        " the Table of Content)",
    )

    IsAuraBow = Symbol(
        [0xCC14],
        [0x200CC14],
        None,
        "Checks if an item is one of the aura bows received at the start of the"
        " game.\n\nr0: item ID\nreturn: bool",
    )

    SprintfStatic = Symbol(
        [
            0xD634,
            0xE990,
            0x13758,
            0x176E4,
            0x17A40,
            0x23590,
            0x2378C,
            0x37F30,
            0x39438,
            0x3CFA4,
            0x42A84,
            0x52418,
            0x54A60,
            0x609E8,
        ],
        [
            0x200D634,
            0x200E990,
            0x2013758,
            0x20176E4,
            0x2017A40,
            0x2023590,
            0x202378C,
            0x2037F30,
            0x2039438,
            0x203CFA4,
            0x2042A84,
            0x2052418,
            0x2054A60,
            0x20609E8,
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
        [0xED1C],
        [0x200ED1C],
        None,
        "Sets the amount of money the player is carrying, clamping the value to the"
        " range [0, MAX_MONEY_CARRIED].\n\nr0: new value",
    )

    IsBagFull = Symbol(
        [0xEDC0],
        [0x200EDC0],
        None,
        "Implements SPECIAL_PROC_IS_BAG_FULL (see ScriptSpecialProcessCall).\n\nreturn:"
        " bool",
    )

    CountItemTypeInBag = Symbol(
        [0xEE88],
        [0x200EE88],
        None,
        "Implements SPECIAL_PROC_COUNT_ITEM_TYPE_IN_BAG (see"
        " ScriptSpecialProcessCall).\n\nr0: item ID\nreturn: number of items of the"
        " specified ID in the bag",
    )

    AddItemToBag = Symbol(
        [0xF84C],
        [0x200F84C],
        None,
        "Implements SPECIAL_PROC_ADD_ITEM_TO_BAG (see ScriptSpecialProcessCall).\n\nr0:"
        " pointer to an owned_item\nreturn: bool",
    )

    ScriptSpecialProcess0x39 = Symbol(
        [0xFD54],
        [0x200FD54],
        None,
        "Implements SPECIAL_PROC_0x39 (see ScriptSpecialProcessCall).\n\nreturn: bool",
    )

    CountItemTypeInStorage = Symbol(
        [0xFEE4],
        [0x200FEE4],
        None,
        "Implements SPECIAL_PROC_COUNT_ITEM_TYPE_IN_STORAGE (see"
        " ScriptSpecialProcessCall).\n\nr0: pointer to an owned_item\nreturn: number of"
        " items of the specified ID in storage",
    )

    RemoveItemsTypeInStorage = Symbol(
        [0x101E4],
        [0x20101E4],
        None,
        "Probably? Implements SPECIAL_PROC_0x2A (see ScriptSpecialProcessCall).\n\nr0:"
        " pointer to an owned_item\nreturn: bool",
    )

    AddItemToStorage = Symbol(
        [0x1031C],
        [0x201031C],
        None,
        "Implements SPECIAL_PROC_ADD_ITEM_TO_STORAGE (see"
        " ScriptSpecialProcessCall).\n\nr0: pointer to an owned_item\nreturn: bool",
    )

    SetMoneyStored = Symbol(
        [0x10724],
        [0x2010724],
        None,
        "Sets the amount of money the player has stored in the Duskull Bank, clamping"
        " the value to the range [0, MAX_MONEY_STORED].\n\nr0: new value",
    )

    GetExclusiveItemOffset = Symbol(
        [0x10E40],
        [0x2010E40],
        None,
        "Gets the exclusive item offset, which is the item ID relative to that of the"
        " first exclusive item, the Prism Ruff.\n\nr0: item ID\nreturn: offset",
    )

    ApplyExclusiveItemStatBoosts = Symbol(
        [0x10E64],
        [0x2010E64],
        None,
        "Applies stat boosts from an exclusive item.\n\nr0: item ID\nr1: pointer to"
        " attack stat to modify\nr2: pointer to special attack stat to modify\nr3:"
        " pointer to defense stat to modify\nstack[0]: pointer to special defense stat"
        " to modify",
    )

    SetExclusiveItemEffect = Symbol(
        [0x10F80],
        [0x2010F80],
        None,
        "Sets the bit for an exclusive item effect.\n\nr0: pointer to the effects"
        " bitvector to modify\nr1: exclusive item effect ID",
    )

    ExclusiveItemEffectFlagTest = Symbol(
        [0x10FA4],
        [0x2010FA4],
        None,
        "Tests the exclusive item bitvector for a specific exclusive item"
        " effect.\n\nr0: the effects bitvector to test\nr1: exclusive item effect"
        " ID\nreturn: bool",
    )

    ApplyGummiBoostsGroundMode = Symbol(
        [0x1189C],
        [0x201189C],
        None,
        "Applies the IQ boosts from eating a Gummi to the target monster.\n\nr0:"
        " Pointer to something\nr1: Pointer to something\nr2: Pointer to something\nr3:"
        " Pointer to something\nstack[0]: ?\nstack[1]: ?\nstack[2]: Pointer to a buffer"
        " to store some result into",
    )

    GetMoveTargetAndRange = Symbol(
        [0x13840],
        [0x2013840],
        None,
        "Gets the move target-and-range field. See struct move_target_and_range in the"
        " C headers.\n\nr0: move pointer\nr1: AI flag (every move has two"
        " target-and-range fields, one for players and one for AI)\nreturn: move target"
        " and range",
    )

    GetMoveType = Symbol(
        [0x13864],
        [0x2013864],
        None,
        "Gets the type of a move\n\nr0: Pointer to move data\nreturn: Type of the move",
    )

    GetMoveAiWeight = Symbol(
        [0x1398C],
        [0x201398C],
        None,
        "Gets the AI weight of a move\n\nr0: Pointer to move data\nreturn: AI weight of"
        " the move",
    )

    GetMoveBasePower = Symbol(
        [0x139CC],
        [0x20139CC],
        None,
        "Gets the base power of a move from the move data table.\n\nr0: move"
        " pointer\nreturn: base power",
    )

    GetMoveAccuracyOrAiChance = Symbol(
        [0x13A0C],
        [0x2013A0C],
        None,
        "Gets one of the two accuracy values of a move or its"
        " ai_condition_random_chance field.\n\nr0: Move pointer\nr1: 0 to get the"
        " move's first accuracy1 field, 1 to get its accuracy2, 2 to get its"
        " ai_condition_random_chance.\nreturn: Move's accuracy1, accuracy2 or"
        " ai_condition_random_chance",
    )

    GetMaxPp = Symbol(
        [0x13A50],
        [0x2013A50],
        None,
        "Gets the maximum PP for a given move.\n\nr0: move pointer\nreturn: max PP for"
        " the given move, capped at 99",
    )

    GetMoveCritChance = Symbol(
        [0x13B10],
        [0x2013B10],
        None,
        "Gets the critical hit chance of a move.\n\nr0: move pointer\nreturn: base"
        " power",
    )

    IsMoveRangeString19 = Symbol(
        [0x13C04],
        [0x2013C04],
        None,
        "Returns whether a move's range string is 19 ('User').\n\nr0: Move"
        " pointer\nreturn: True if the move's range string field has a value of 19.",
    )

    IsRecoilMove = Symbol(
        [0x13E14],
        [0x2013E14],
        None,
        "Checks if the given move is a recoil move (affected by Reckless).\n\nr0: move"
        " ID\nreturn: bool",
    )

    IsPunchMove = Symbol(
        [0x14D18],
        [0x2014D18],
        None,
        "Checks if the given move is a punch move (affected by Iron Fist).\n\nr0: move"
        " ID\nreturn: bool",
    )

    GetMoveCategory = Symbol(
        [0x151C8],
        [0x20151C8],
        None,
        "Gets a move's category (physical, special, status).\n\nr0: move ID\nreturn:"
        " move category enum",
    )

    LoadWteFromRom = Symbol(
        [0x1DE4C],
        [0x201DE4C],
        None,
        "Loads a SIR0-wrapped WTE file from ROM, and returns a handle to it\n\nr0:"
        " [output] pointer to wte handle\nr1: file path string\nr2: load file flags",
    )

    LoadWteFromFileDirectory = Symbol(
        [0x1DEC4],
        [0x201DEC4],
        None,
        "Loads a SIR0-wrapped WTE file from a file directory, and returns a handle to"
        " it\n\nr0: [output] pointer to wte handle\nr1: file directory id\nr2: file"
        " index\nr3: malloc flags",
    )

    UnloadWte = Symbol(
        [0x1DF18],
        [0x201DF18],
        None,
        "Frees the buffer used to store the WTE data in the handle, and sets both"
        " pointers to null\n\nr0: pointer to wte handle",
    )

    HandleSir0Translation = Symbol(
        [0x1F4B4],
        [0x201F4B4],
        None,
        "Translates the offsets in a SIR0 file into NDS memory addresses, changes the"
        " magic number to SirO (opened), and returns a pointer to the first pointer"
        " specified in the SIR0 header (beginning of the data).\n\nr0: [output] double"
        " pointer to beginning of data\nr1: pointer to source file buffer",
    )

    HandleSir0TranslationVeneer = Symbol(
        [0x1F58C],
        [0x201F58C],
        None,
        "Likely a linker-generated veneer for HandleSir0Translation.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nr0:"
        " [output] double pointer to beginning of data\nr1: pointer to source file"
        " buffer",
    )

    GetLanguageType = Symbol(
        [0x205A0],
        [0x20205A0],
        None,
        "Gets the language type.\n\nThis is the value backing the special LANGUAGE_TYPE"
        " script variable.\n\nreturn: language type",
    )

    GetLanguage = Symbol(
        [0x205B0],
        [0x20205B0],
        None,
        "Gets the single-byte language ID of the current program.\n\nThe language ID"
        " appears to be used to index some global tables.\n\nreturn: language ID",
    )

    PreprocessString = Symbol(
        [0x223F0],
        [0x20223F0],
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
        [0x25100],
        [0x2025100],
        None,
        "A simple implementation of the strcpy(3) C library function.\n\nThis function"
        " was probably manually implemented by the developers. See Strcpy for what's"
        " probably the real libc function.\n\nr0: dest\nr1: src",
    )

    StrncpySimple = Symbol(
        [0x2511C],
        [0x202511C],
        None,
        "A simple implementation of the strncpy(3) C library function.\n\nThis function"
        " was probably manually implemented by the developers. See Strncpy for what's"
        " probably the real libc function.\n\nr0: dest\nr1: src\nr2: n",
    )

    StringFromMessageId = Symbol(
        [0x258C4],
        [0x20258C4],
        None,
        "Gets the string corresponding to a given message ID.\n\nr0: message"
        " ID\nreturn: string from the string files with the given message ID",
    )

    SetScreenWindowsColor = Symbol(
        [0x27A68],
        [0x2027A68],
        None,
        "Sets the palette of the frames of windows in the specified screen\n\nr0:"
        " palette index\nr1: is upper screen",
    )

    SetBothScreensWindowsColor = Symbol(
        [0x27A80],
        [0x2027A80],
        None,
        "Sets the palette of the frames of windows in both screens\n\nr0: palette"
        " index",
    )

    GetNotifyNote = Symbol(
        [0x484A0],
        [0x20484A0],
        None,
        "Returns the current value of NOTIFY_NOTE.\n\nreturn: bool",
    )

    SetNotifyNote = Symbol(
        [0x484B0], [0x20484B0], None, "Sets NOTIFY_NOTE to the given value.\n\nr0: bool"
    )

    InitMainTeamAfterQuiz = Symbol(
        [0x487C4],
        [0x20487C4],
        None,
        "Implements SPECIAL_PROC_INIT_MAIN_TEAM_AFTER_QUIZ (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x3 = Symbol(
        [0x48A0C],
        [0x2048A0C],
        None,
        "Implements SPECIAL_PROC_0x3 (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x4 = Symbol(
        [0x48A84],
        [0x2048A84],
        None,
        "Implements SPECIAL_PROC_0x4 (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    NoteSaveBase = Symbol(
        [0x48F84],
        [0x2048F84],
        None,
        "Probably related to saving or quicksaving?\n\nThis function prints the debug"
        " message 'NoteSave Base %d %d' with some values. It's also the only place"
        " where GetRngSeed is called.\n\nr0: possibly a flag/code that controls the"
        " type of save file to generate?\nothers: ?\nreturn: status code",
    )

    NoteLoadBase = Symbol(
        [0x49370],
        [0x2049370],
        None,
        "Probably related to loading a save file or quicksave?\n\nThis function prints"
        " the debug message 'NoteLoad Base %d' with some value. It's also the only"
        " place where SetRngSeed is called.\n\nreturn: status code",
    )

    GetGameMode = Symbol(
        [0x4AFC0],
        [0x204AFC0],
        None,
        "Gets the value of GAME_MODE.\n\nreturn: game mode",
    )

    InitScriptVariableValues = Symbol(
        [0x4B04C],
        [0x204B04C],
        None,
        "Initialize the script variable values table (SCRIPT_VARS_VALUES).\n\nThe whole"
        " table is first zero-initialized. Then, all script variable values are first"
        " initialized to their defaults, after which some of them are overwritten with"
        " other hard-coded values.\n\nNo params.",
    )

    InitEventFlagScriptVars = Symbol(
        [0x4B304],
        [0x204B304],
        None,
        "Initializes an assortment of event flag script variables (see the code for an"
        " exhaustive list).\n\nNo params.",
    )

    ZinitScriptVariable = Symbol(
        [0x4B434],
        [0x204B434],
        None,
        "Zero-initialize the values of the given script variable.\n\nr0: pointer to the"
        " local variable table (only needed if id >= VAR_LOCAL0)\nr1: script"
        " variable ID",
    )

    LoadScriptVariableRaw = Symbol(
        [0x4B49C],
        [0x204B49C],
        None,
        "Loads a script variable descriptor for a given ID.\n\nr0: [output] script"
        " variable descriptor pointer\nr1: pointer to the local variable table (doesn't"
        " need to be valid; just controls the output value pointer)\nr2: script"
        " variable ID",
    )

    LoadScriptVariableValue = Symbol(
        [0x4B4EC],
        [0x204B4EC],
        None,
        "Loads the value of a script variable.\n\nr0: pointer to the local variable"
        " table (only needed if id >= VAR_LOCAL0)\nr1: script variable ID\nreturn:"
        " value",
    )

    LoadScriptVariableValueAtIndex = Symbol(
        [0x4B678],
        [0x204B678],
        None,
        "Loads the value of a script variable at some index (for script variables that"
        " are arrays).\n\nr0: pointer to the local variable table (only needed if id >="
        " VAR_LOCAL0)\nr1: script variable ID\nr2: value index for the given script"
        " var\nreturn: value",
    )

    SaveScriptVariableValue = Symbol(
        [0x4B820],
        [0x204B820],
        None,
        "Saves the given value to a script variable.\n\nr0: pointer to local variable"
        " table (only needed if id >= VAR_LOCAL0)\nr1: script variable ID\nr2: value to"
        " save",
    )

    SaveScriptVariableValueAtIndex = Symbol(
        [0x4B988],
        [0x204B988],
        None,
        "Saves the given value to a script variable at some index (for script variables"
        " that are arrays).\n\nr0: pointer to local variable table (only needed if id"
        " >= VAR_LOCAL0)\nr1: script variable ID\nr2: value index for the given script"
        " var\nr3: value to save",
    )

    LoadScriptVariableValueSum = Symbol(
        [0x4BB00],
        [0x204BB00],
        None,
        "Loads the sum of all values of a given script variable (for script variables"
        " that are arrays).\n\nr0: pointer to the local variable table (only needed if"
        " id >= VAR_LOCAL0)\nr1: script variable ID\nreturn: sum of values",
    )

    LoadScriptVariableValueBytes = Symbol(
        [0x4BB64],
        [0x204BB64],
        None,
        "Loads some number of bytes from the value of a given script variable.\n\nr0:"
        " script variable ID\nr1: [output] script variable value bytes\nr2: number of"
        " bytes to load",
    )

    SaveScriptVariableValueBytes = Symbol(
        [0x4BBCC],
        [0x204BBCC],
        None,
        "Saves some number of bytes to the given script variable.\n\nr0: script"
        " variable ID\nr1: bytes to save\nr2: number of bytes",
    )

    ScriptVariablesEqual = Symbol(
        [0x4BC18],
        [0x204BC18],
        None,
        "Checks if two script variables have equal values. For arrays, compares"
        " elementwise for the length of the first variable.\n\nr0: pointer to the local"
        " variable table (only needed if id >= VAR_LOCAL0)\nr1: script variable ID"
        " 1\nr2: script variable ID 2\nreturn: true if values are equal, false"
        " otherwise",
    )

    EventFlagBackup = Symbol(
        [0x4C1E4],
        [0x204C1E4],
        None,
        "Saves event flag script variables (see the code for an exhaustive list) to"
        " their respective BACKUP script variables, but only in certain game"
        " modes.\n\nThis function prints the debug string 'EventFlag BackupGameMode %d'"
        " with the game mode.\n\nNo params.",
    )

    DumpScriptVariableValues = Symbol(
        [0x4C408],
        [0x204C408],
        None,
        "Runs EventFlagBackup, then copies the script variable values table"
        " (SCRIPT_VARS_VALUES) to the given pointer.\n\nr0: destination pointer for the"
        " data dump\nreturn: always 1",
    )

    RestoreScriptVariableValues = Symbol(
        [0x4C430],
        [0x204C430],
        None,
        "Restores the script variable values table (SCRIPT_VARS_VALUES) with the given"
        " data. The source data is assumed to be exactly 1024 bytes in length.\n\nr0:"
        " raw data to copy to the values table\nreturn: whether the restored value for"
        " VAR_VERSION is equal to its default value",
    )

    InitScenarioScriptVars = Symbol(
        [0x4C488],
        [0x204C488],
        None,
        "Initializes most of the SCENARIO_* script variables (except"
        " SCENARIO_TALK_BIT_FLAG for some reason). Also initializes the PLAY_OLD_GAME"
        " variable.\n\nNo params.",
    )

    SetScenarioScriptVar = Symbol(
        [0x4C618],
        [0x204C618],
        None,
        "Sets the given SCENARIO_* script variable with a given pair of values [val0,"
        " val1].\n\nIn the special case when the ID is VAR_SCENARIO_MAIN, and the set"
        " value is different from the old one, the REQUEST_CLEAR_COUNT script variable"
        " will be set to 0.\n\nr0: script variable ID\nr1: val0\nr2: val1",
    )

    GetSpecialEpisodeType = Symbol(
        [0x4C8EC],
        [0x204C8EC],
        None,
        "Gets the special episode type from the SPECIAL_EPISODE_TYPE script"
        " variable.\n\nreturn: special episode type",
    )

    ScenarioFlagBackup = Symbol(
        [0x4CCB8],
        [0x204CCB8],
        None,
        "Saves scenario flag script variables (SCENARIO_SELECT, SCENARIO_MAIN_BIT_FLAG)"
        " to their respective BACKUP script variables, but only in certain game"
        " modes.\n\nThis function prints the debug string 'ScenarioFlag BackupGameMode"
        " %d' with the game mode.\n\nNo params.",
    )

    InitWorldMapScriptVars = Symbol(
        [0x4CD88],
        [0x204CD88],
        None,
        "Initializes the WORLD_MAP_* script variable values (IDs 0x55-0x57).\n\nNo"
        " params.",
    )

    InitDungeonListScriptVars = Symbol(
        [0x4CE90],
        [0x204CE90],
        None,
        "Initializes the DUNGEON_*_LIST script variable values (IDs 0x4f-0x54).\n\nNo"
        " params.",
    )

    SetDungeonTipShown = Symbol(
        [0x4D250],
        [0x204D250],
        None,
        "Marks a dungeon tip as already shown to the player\n\nr0: Dungeon tip ID",
    )

    GetDungeonTipShown = Symbol(
        [0x4D290],
        [0x204D290],
        None,
        "Checks if a dungeon tip has already been shown before or not.\n\nr0: Dungeon"
        " tip ID\nreturn: True if the tip has been shown before, false otherwise.",
    )

    MonsterSpawnsEnabled = Symbol(
        [0x4D360],
        [0x204D360],
        None,
        "Always returns true.\n\nThis function seems to be a debug switch that the"
        " developers may have used to disable the random enemy spawn. \nIf it returned"
        " false, the call to SpawnMonster inside TrySpawnMonsterAndTickSpawnCounter"
        " would not be executed.\n\nreturn: bool (always true)",
    )

    SetAdventureLogStructLocation = Symbol(
        [0x4FA24],
        [0x204FA24],
        None,
        "Sets the location of the adventure log struct in memory.\n\nSets it in a"
        " static memory location (At 0x22AB69C [US], 0x22ABFDC [EU], 0x22ACE58"
        " [JP])\n\nNo params.",
    )

    SetAdventureLogDungeonFloor = Symbol(
        [0x4FA3C],
        [0x204FA3C],
        None,
        "Sets the current dungeon floor pair.\n\nr0: struct dungeon_floor_pair",
    )

    GetAdventureLogDungeonFloor = Symbol(
        [0x4FA5C],
        [0x204FA5C],
        None,
        "Gets the current dungeon floor pair.\n\nreturn: struct dungeon_floor_pair",
    )

    ClearAdventureLogStruct = Symbol(
        [0x4FA70],
        [0x204FA70],
        None,
        "Clears the adventure log structure.\n\nNo params.",
    )

    SetAdventureLogCompleted = Symbol(
        [0x4FB9C],
        [0x204FB9C],
        None,
        "Marks one of the adventure log entry as completed.\n\nr0: entry ID",
    )

    IsAdventureLogNotEmpty = Symbol(
        [0x4FBC4],
        [0x204FBC4],
        None,
        "Checks if at least one of the adventure log entry is completed.\n\nreturn:"
        " bool",
    )

    GetAdventureLogCompleted = Symbol(
        [0x4FBFC],
        [0x204FBFC],
        None,
        "Checks if one adventure log entry is completed.\n\nr0: entry ID\nreturn: bool",
    )

    IncrementNbDungeonsCleared = Symbol(
        [0x4FC28],
        [0x204FC28],
        None,
        "Increments by 1 the number of dungeons cleared.\n\nImplements"
        " SPECIAL_PROC_0x3A (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    GetNbDungeonsCleared = Symbol(
        [0x4FC6C],
        [0x204FC6C],
        None,
        "Gets the number of dungeons cleared.\n\nreturn: the number of dungeons"
        " cleared",
    )

    IncrementNbFriendRescues = Symbol(
        [0x4FC80],
        [0x204FC80],
        None,
        "Increments by 1 the number of successful friend rescues.\n\nNo params.",
    )

    GetNbFriendRescues = Symbol(
        [0x4FCC8],
        [0x204FCC8],
        None,
        "Gets the number of successful friend rescues.\n\nreturn: the number of"
        " successful friend rescues",
    )

    IncrementNbEvolutions = Symbol(
        [0x4FCDC],
        [0x204FCDC],
        None,
        "Increments by 1 the number of evolutions.\n\nNo params.",
    )

    GetNbEvolutions = Symbol(
        [0x4FD24],
        [0x204FD24],
        None,
        "Gets the number of evolutions.\n\nreturn: the number of evolutions",
    )

    IncrementNbSteals = Symbol(
        [0x4FD38],
        [0x204FD38],
        None,
        "Leftover from Time & Darkness. Does not do anything.\n\nCalls to this matches"
        " the ones for incrementing the number of successful steals in Time &"
        " Darkness.\n\nNo params.",
    )

    IncrementNbEggsHatched = Symbol(
        [0x4FD3C],
        [0x204FD3C],
        None,
        "Increments by 1 the number of eggs hatched.\n\nNo params.",
    )

    GetNbEggsHatched = Symbol(
        [0x4FD78],
        [0x204FD78],
        None,
        "Gets the number of eggs hatched.\n\nreturn: the number of eggs hatched",
    )

    GetNbPokemonJoined = Symbol(
        [0x4FD8C],
        [0x204FD8C],
        None,
        "Gets the number of different pokémon that joined.\n\nreturn: the number of"
        " different pokémon that joined",
    )

    GetNbMovesLearned = Symbol(
        [0x4FDA0],
        [0x204FDA0],
        None,
        "Gets the number of different moves learned.\n\nreturn: the number of different"
        " moves learned",
    )

    SetVictoriesOnOneFloor = Symbol(
        [0x4FDB4],
        [0x204FDB4],
        None,
        "Sets the record of victories on one floor.\n\nr0: the new record of victories",
    )

    GetVictoriesOnOneFloor = Symbol(
        [0x4FDE8],
        [0x204FDE8],
        None,
        "Gets the record of victories on one floor.\n\nreturn: the record of victories",
    )

    SetPokemonJoined = Symbol(
        [0x4FDFC], [0x204FDFC], None, "Marks one pokémon as joined.\n\nr0: monster ID"
    )

    SetPokemonBattled = Symbol(
        [0x4FE58], [0x204FE58], None, "Marks one pokémon as battled.\n\nr0: monster ID"
    )

    GetNbPokemonBattled = Symbol(
        [0x4FEB4],
        [0x204FEB4],
        None,
        "Gets the number of different pokémon that battled against you.\n\nreturn: the"
        " number of different pokémon that battled against you",
    )

    IncrementNbBigTreasureWins = Symbol(
        [0x4FEC8],
        [0x204FEC8],
        None,
        "Increments by 1 the number of big treasure wins.\n\nImplements"
        " SPECIAL_PROC_0x3B (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    SetNbBigTreasureWins = Symbol(
        [0x4FEE8],
        [0x204FEE8],
        None,
        "Sets the number of big treasure wins.\n\nr0: the new number of big treasure"
        " wins",
    )

    GetNbBigTreasureWins = Symbol(
        [0x4FF20],
        [0x204FF20],
        None,
        "Gets the number of big treasure wins.\n\nreturn: the number of big treasure"
        " wins",
    )

    SetNbRecycled = Symbol(
        [0x4FF34],
        [0x204FF34],
        None,
        "Sets the number of items recycled.\n\nr0: the new number of items recycled",
    )

    GetNbRecycled = Symbol(
        [0x4FF6C],
        [0x204FF6C],
        None,
        "Gets the number of items recycled.\n\nreturn: the number of items recycled",
    )

    IncrementNbSkyGiftsSent = Symbol(
        [0x4FF80],
        [0x204FF80],
        None,
        "Increments by 1 the number of sky gifts sent.\n\nImplements"
        " SPECIAL_PROC_SEND_SKY_GIFT_TO_GUILDMASTER (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    SetNbSkyGiftsSent = Symbol(
        [0x4FFA0],
        [0x204FFA0],
        None,
        "Sets the number of Sky Gifts sent.\n\nreturn: the number of Sky Gifts sent",
    )

    GetNbSkyGiftsSent = Symbol(
        [0x4FFD8],
        [0x204FFD8],
        None,
        "Gets the number of Sky Gifts sent.\n\nreturn: the number of Sky Gifts sent",
    )

    ComputeSpecialCounters = Symbol(
        [0x4FFEC],
        [0x204FFEC],
        None,
        "Computes the counters from the bit fields in the adventure log, as they are"
        " not updated automatically when bit fields are altered.\n\nAffects"
        " GetNbPokemonJoined, GetNbMovesLearned, GetNbPokemonBattled and"
        " GetNbItemAcquired.\n\nNo params.",
    )

    RecruitSpecialPokemonLog = Symbol(
        [0x50244],
        [0x2050244],
        None,
        "Marks a specified special pokémon as recruited in the adventure log.\n\nr0:"
        " monster ID",
    )

    IncrementNbFainted = Symbol(
        [0x502B0],
        [0x20502B0],
        None,
        "Increments by 1 the number of times you fainted.\n\nNo params.",
    )

    GetNbFainted = Symbol(
        [0x502EC],
        [0x20502EC],
        None,
        "Gets the number of times you fainted.\n\nreturn: the number of times you"
        " fainted",
    )

    SetItemAcquired = Symbol(
        [0x50300],
        [0x2050300],
        None,
        "Marks one specific item as acquired.\n\nr0: item ID",
    )

    GetNbItemAcquired = Symbol(
        [0x503CC],
        [0x20503CC],
        None,
        "Gets the number of items acquired.\n\nreturn: the number of items acquired",
    )

    SetChallengeLetterCleared = Symbol(
        [0x50420],
        [0x2050420],
        None,
        "Sets a challenge letter as cleared.\n\nr0: challenge ID",
    )

    GetSentryDutyGamePoints = Symbol(
        [0x504A4],
        [0x20504A4],
        None,
        "Gets the points for the associated rank in the footprints minigame.\n\nr0: the"
        " rank (range 0-4, 1st to 5th)\nreturn: points",
    )

    SetSentryDutyGamePoints = Symbol(
        [0x504BC],
        [0x20504BC],
        None,
        "Sets a new record in the footprints minigame.\n\nr0: points\nreturn: the rank"
        " (range 0-4, 1st to 5th; -1 if out of ranking)",
    )

    SubFixedPoint = Symbol(
        [0x50F10],
        [0x2050F10],
        None,
        "Compute the subtraction of two decimal fixed-point numbers (16 fraction"
        " bits).\n\nFloats are in the format {16-bit integer part, 16-bit thousandths},"
        " where the integer part is the lower word. Probably used primarily for"
        " belly.\n\nr0: float\nr1: decrement\nreturn: max(float - decrement, 0)",
    )

    BinToDecFixedPoint = Symbol(
        [0x51020],
        [0x2051020],
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
        [0x51064],
        [0x2051064],
        None,
        "Compute the ceiling of a decimal fixed-point number (16 fraction"
        " bits).\n\nFloats are in the format {16-bit integer part, 16-bit thousandths},"
        " where the integer part is the lower word. Probably used primarily for"
        " belly.\n\nr0: float\nreturn: ceil(float)",
    )

    DungeonGoesUp = Symbol(
        [0x51288],
        [0x2051288],
        None,
        "Returns whether the specified dungeon is considered as going upward or"
        " not\n\nr0: dungeon id\nreturn: bool",
    )

    GetMaxRescueAttempts = Symbol(
        [0x51380],
        [0x2051380],
        None,
        "Returns the maximum rescue attempts allowed in the specified dungeon.\n\nr0:"
        " dungeon id\nreturn: Max rescue attempts, or -1 if rescues are disabled.",
    )

    JoinedAtRangeCheck = Symbol(
        [0x51490],
        [0x2051490],
        None,
        "Returns whether a certain joined_at field value is between"
        " dungeon_id::DUNGEON_JOINED_AT_BIDOOF and"
        " dungeon_id::DUNGEON_DUMMY_0xE3.\n\nr0: joined_at id\nreturn: bool",
    )

    JoinedAtRangeCheck2 = Symbol(
        [0x51760],
        [0x2051760],
        None,
        "Returns whether a certain joined_at field value is equal to"
        " dungeon_id::DUNGEON_BEACH or is between dungeon_id::DUNGEON_DUMMY_0xEC and"
        " dungeon_id::DUNGEON_DUMMY_0xF0.\n\nr0: joined_at id\nreturn: bool",
    )

    GetMonsterGender = Symbol(
        [0x527A8],
        [0x20527A8],
        None,
        "Returns the gender field of a monster given its ID.\n\nr0: monster id\nreturn:"
        " monster gender",
    )

    GetSpriteSize = Symbol(
        [0x527E0],
        [0x20527E0],
        None,
        "Returns the sprite size of the specified monster. If the size is between 1 and"
        " 6, 6 will be returned.\n\nr0: monster id\nreturn: sprite size",
    )

    GetSpriteFileSize = Symbol(
        [0x5281C],
        [0x205281C],
        None,
        "Returns the sprite file size of the specified monster.\n\nr0: monster"
        " id\nreturn: sprite file size",
    )

    GetCanMoveFlag = Symbol(
        [0x528B4],
        [0x20528B4],
        None,
        "Returns the flag that determines if a monster can move in dungeons.\n\nr0:"
        " Monster ID\nreturn: 'Can move' flag",
    )

    GetMonsterPreEvolution = Symbol(
        [0x529A8],
        [0x20529A8],
        None,
        "Returns the pre-evolution id of a monster given its ID.\n\nr0: monster"
        " id\nreturn: ID of the monster that evolves into the one specified in r0",
    )

    GetEvolutions = Symbol(
        [0x53E88],
        [0x2053E88],
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
        [0x54480],
        [0x2054480],
        None,
        "Returns the monster ID of the specified monster spawn entry\n\nr0: Pointer to"
        " the monster spawn entry\nreturn: monster_spawn_entry::id",
    )

    GetMonsterLevelFromSpawnEntry = Symbol(
        [0x544B8],
        [0x20544B8],
        None,
        "Returns the level of the specified monster spawn entry.\n\nr0: pointer to the"
        " monster spawn entry\nreturn: uint8_t",
    )

    GetMonsterGenderVeneer = Symbol(
        [0x54760],
        [0x2054760],
        None,
        "Likely a linker-generated veneer for GetMonsterGender.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nr0:"
        " monster id\nreturn: monster gender",
    )

    IsUnown = Symbol(
        [0x54A88],
        [0x2054A88],
        None,
        "Checks if a monster ID is an Unown.\n\nr0: monster ID\nreturn: bool",
    )

    IsShaymin = Symbol(
        [0x54AA4],
        [0x2054AA4],
        None,
        "Checks if a monster ID is a Shaymin form.\n\nr0: monster ID\nreturn: bool",
    )

    IsCastform = Symbol(
        [0x54AD4],
        [0x2054AD4],
        None,
        "Checks if a monster ID is a Castform form.\n\nr0: monster ID\nreturn: bool",
    )

    IsCherrim = Symbol(
        [0x54B2C],
        [0x2054B2C],
        None,
        "Checks if a monster ID is a Cherrim form.\n\nr0: monster ID\nreturn: bool",
    )

    IsDeoxys = Symbol(
        [0x54B74],
        [0x2054B74],
        None,
        "Checks if a monster ID is a Deoxys form.\n\nr0: monster ID\nreturn: bool",
    )

    IsMonsterOnTeam = Symbol(
        [0x55148],
        [0x2055148],
        None,
        "Checks if a given monster is on the exploration team (not necessarily the"
        " active party)?\n\nr0: monster ID\nr1: ?\nreturn: bool",
    )

    CheckTeamMemberField8 = Symbol(
        [0x56228],
        [0x2056228],
        None,
        "Checks if a value obtained from team_member::field_0x8 is equal to certain"
        " values.\n\nThis is known to return true for some or all of the guest"
        " monsters.\n\nr0: Value read from team_member::field_0x8\nreturn: True if the"
        " value is equal to 0x55AA or 0x5AA5",
    )

    GetTeamMemberData = Symbol(
        [0x5638C],
        [0x205638C],
        None,
        "Returns a struct containing information about a team member.\n\nr0:"
        " Index\nreturn: Pointer to struct containing team member information",
    )

    SetTeamSetupHeroAndPartnerOnly = Symbol(
        [0x569CC],
        [0x20569CC],
        None,
        "Implements SPECIAL_PROC_SET_TEAM_SETUP_HERO_AND_PARTNER_ONLY (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    SetTeamSetupHeroOnly = Symbol(
        [0x56AB0],
        [0x2056AB0],
        None,
        "Implements SPECIAL_PROC_SET_TEAM_SETUP_HERO_ONLY (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    GetPartyMembers = Symbol(
        [0x56C20],
        [0x2056C20],
        None,
        "Appears to get the team's active party members. Implements most of"
        " SPECIAL_PROC_IS_TEAM_SETUP_SOLO (see ScriptSpecialProcessCall).\n\nr0:"
        " [output] Array of 4 2-byte values (they seem to be indexes of some sort)"
        " describing each party member, which will be filled in by the function. The"
        " input can be a null pointer if the party members aren't needed\nreturn:"
        " Number of party members",
    )

    IqSkillFlagTest = Symbol(
        [0x58F04],
        [0x2058F04],
        None,
        "Tests whether an IQ skill with a given ID is active.\n\nr0: IQ skill bitvector"
        " to test\nr1: IQ skill ID\nreturn: bool",
    )

    GetExplorerMazeMonster = Symbol(
        [0x590F8],
        [0x20590F8],
        None,
        "Returns the data of a monster sent into the Explorer Dojo using the 'exchange"
        " teams' option.\n\nr0: Entry number (0-3)\nreturn: Ground monster data of the"
        " specified entry",
    )

    GetSosMailCount = Symbol(
        [0x5B97C],
        [0x205B97C],
        None,
        "Implements SPECIAL_PROC_GET_SOS_MAIL_COUNT (see"
        " ScriptSpecialProcessCall).\n\nr0: ?\nr1: some flag?\nreturn: SOS mail count",
    )

    DungeonRequestsDone = Symbol(
        [0x5EDA4],
        [0x205EDA4],
        None,
        "Seems to return the number of missions completed.\n\nPart of the"
        " implementation for SPECIAL_PROC_DUNGEON_HAD_REQUEST_DONE (see"
        " ScriptSpecialProcessCall).\n\nr0: ?\nr1: some flag?\nreturn: number of"
        " missions completed",
    )

    DungeonRequestsDoneWrapper = Symbol(
        [0x5EE10],
        [0x205EE10],
        None,
        "Calls DungeonRequestsDone with the second argument set to false.\n\nr0:"
        " ?\nreturn: number of mission completed",
    )

    AnyDungeonRequestsDone = Symbol(
        [0x5EE20],
        [0x205EE20],
        None,
        "Calls DungeonRequestsDone with the second argument set to true, and converts"
        " the integer output to a boolean.\n\nr0: ?\nreturn: bool: whether the number"
        " of missions completed is greater than 0",
    )

    ScriptSpecialProcess0x3D = Symbol(
        [0x65B50],
        [0x2065B50],
        None,
        "Implements SPECIAL_PROC_0x3D (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x3E = Symbol(
        [0x65B60],
        [0x2065B60],
        None,
        "Implements SPECIAL_PROC_0x3E (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x17 = Symbol(
        [0x65C48],
        [0x2065C48],
        None,
        "Implements SPECIAL_PROC_0x17 (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ItemAtTableIdx = Symbol(
        [0x65CF8],
        [0x2065CF8],
        None,
        "Gets info about the item at a given item table (not sure what this table"
        " is...) index.\n\nUsed by SPECIAL_PROC_COUNT_TABLE_ITEM_TYPE_IN_BAG and"
        " friends (see ScriptSpecialProcessCall).\n\nr0: table index\nr1: [output]"
        " pointer to an owned_item",
    )

    WaitForInterrupt = Symbol(
        [0x7BC30],
        [0x207BC30],
        None,
        "Presumably blocks until the program receives an interrupt.\n\nThis just calls"
        " (in Ghidra terminology) coproc_moveto_Wait_for_interrupt(0). See"
        " https://en.wikipedia.org/wiki/ARM_architecture_family#Coprocessors.\n\nNo"
        " params.",
    )

    FileInit = Symbol(
        [0x7F3E4],
        [0x207F3E4],
        None,
        "Initializes a file_stream structure for file I/O.\n\nThis function must always"
        " be called before opening a file.\n\nr0: file_stream pointer",
    )

    Abs = Symbol(
        [0x8655C],
        [0x208655C],
        None,
        "Takes the absolute value of an integer.\n\nr0: x\nreturn: abs(x)",
    )

    Mbtowc = Symbol(
        [0x871BC],
        [0x20871BC],
        None,
        "The mbtowc(3) C library function.\n\nr0: pwc\nr1: s\nr2: n\nreturn: number of"
        " consumed bytes, or -1 on failure",
    )

    TryAssignByte = Symbol(
        [0x871F4],
        [0x20871F4],
        None,
        "Assign a byte to the target of a pointer if the pointer is non-null.\n\nr0:"
        " pointer\nr1: value\nreturn: true on success, false on failure",
    )

    TryAssignByteWrapper = Symbol(
        [0x87208],
        [0x2087208],
        None,
        "Wrapper around TryAssignByte.\n\nAccesses the TryAssignByte function with a"
        " weird chain of pointer dereferences.\n\nr0: pointer\nr1: value\nreturn: true"
        " on success, false on failure",
    )

    Wcstombs = Symbol(
        [0x87224],
        [0x2087224],
        None,
        "The wcstombs(3) C library function.\n\nr0: dest\nr1: src\nr2: n\nreturn:"
        " characters converted",
    )

    Memcpy = Symbol(
        [0x8729C],
        [0x208729C],
        None,
        "The memcpy(3) C library function.\n\nr0: dest\nr1: src\nr2: n",
    )

    Memmove = Symbol(
        [0x872BC],
        [0x20872BC],
        None,
        "The memmove(3) C library function.\n\nThe implementation is nearly the same as"
        " Memcpy, but it copies bytes from back to front if src < dst.\n\nr0: dest\nr1:"
        " src\nr2: n",
    )

    Memset = Symbol(
        [0x87308],
        [0x2087308],
        None,
        "The memset(3) C library function.\n\nThis is just a wrapper around"
        " MemsetInternal that returns the pointer at the end.\n\nr0: s\nr1: c (int, but"
        " must be a single-byte value)\nr2: n\nreturn: s",
    )

    Memchr = Symbol(
        [0x8731C],
        [0x208731C],
        None,
        "The memchr(3) C library function.\n\nr0: s\nr1: c\nr2: n\nreturn: pointer to"
        " first occurrence of c in s, or a null pointer if no match",
    )

    Memcmp = Symbol(
        [0x87348],
        [0x2087348],
        None,
        "The memcmp(3) C library function.\n\nr0: s1\nr1: s2\nr2: n\nreturn: comparison"
        " value",
    )

    MemsetInternal = Symbol(
        [0x87388],
        [0x2087388],
        None,
        "The actual memory-setting implementation for the memset(3) C library"
        " function.\n\nThis function is optimized to set bytes in 4-byte chunks for n"
        " >= 32, correctly handling any unaligned bytes at the front/back. In this"
        " case, it also further optimizes by unrolling a for loop to set 8 4-byte"
        " values at once (effectively a 32-byte chunk).\n\nr0: s\nr1: c (int, but must"
        " be a single-byte value)\nr2: n",
    )

    VsprintfInternalSlice = Symbol(
        [0x88C74],
        [0x2088C74],
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
        [0x89498],
        [0x2089498],
        None,
        "Best-effort append the given data to a slice. If the slice's capacity is"
        " reached, any remaining data will be truncated.\n\nr0: slice pointer\nr1:"
        " buffer of data to append\nr2: number of bytes in the data buffer\nreturn:"
        " true",
    )

    VsprintfInternal = Symbol(
        [0x894DC],
        [0x20894DC],
        None,
        "This is what implements Vsprintf. It's akin to __vsprintf_internal in the"
        " modern-day version of glibc (in fact, it's probably an older version of"
        " this).\n\nr0: str\nr1: maxlen (Vsprintf passes UINT32_MAX for this)\nr2:"
        " format\nr3: ap\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    Vsprintf = Symbol(
        [0x89544],
        [0x2089544],
        None,
        "The vsprintf(3) C library function.\n\nr0: str\nr1: format\nr2: ap\nreturn:"
        " number of characters printed, excluding the null-terminator",
    )

    Snprintf = Symbol(
        [0x8955C],
        [0x208955C],
        None,
        "The snprintf(3) C library function.\n\nThis calls VsprintfInternal directly,"
        " so it's presumably the real snprintf.\n\nr0: str\nr1: n\nr2: format\n...:"
        " variadic\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    Sprintf = Symbol(
        [0x89584],
        [0x2089584],
        None,
        "The sprintf(3) C library function.\n\nThis calls VsprintfInternal directly, so"
        " it's presumably the real sprintf.\n\nr0: str\nr1: format\n...:"
        " variadic\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    Strlen = Symbol(
        [0x89678],
        [0x2089678],
        None,
        "The strlen(3) C library function.\n\nr0: s\nreturn: length of s",
    )

    Strcpy = Symbol(
        [0x89694],
        [0x2089694],
        None,
        "The strcpy(3) C library function.\n\nThis function is optimized to copy"
        " characters in aligned 4-byte chunks if possible, correctly handling any"
        " unaligned bytes at the front/back.\n\nr0: dest\nr1: src",
    )

    Strncpy = Symbol(
        [0x8975C],
        [0x208975C],
        None,
        "The strncpy(3) C library function.\n\nr0: dest\nr1: src\nr2: n",
    )

    Strcat = Symbol(
        [0x897AC],
        [0x20897AC],
        None,
        "The strcat(3) C library function.\n\nr0: dest\nr1: src",
    )

    Strncat = Symbol(
        [0x897DC],
        [0x20897DC],
        None,
        "The strncat(3) C library function.\n\nr0: dest\nr1: src\nr2: n",
    )

    Strcmp = Symbol(
        [0x8982C],
        [0x208982C],
        None,
        "The strcmp(3) C library function.\n\nSimilarly to Strcpy, this function is"
        " optimized to compare characters in aligned 4-byte chunks if possible.\n\nr0:"
        " s1\nr1: s2\nreturn: comparison value",
    )

    Strncmp = Symbol(
        [0x89940],
        [0x2089940],
        None,
        "The strncmp(3) C library function.\n\nr0: s1\nr1: s2\nr2: n\nreturn:"
        " comparison value",
    )

    Strchr = Symbol(
        [0x89974],
        [0x2089974],
        None,
        "The strchr(3) C library function.\n\nr0: string\nr1: c\nreturn: pointer to the"
        " located byte c, or null pointer if no match",
    )

    Strcspn = Symbol(
        [0x899B0],
        [0x20899B0],
        None,
        "The strcspn(3) C library function.\n\nr0: string\nr1: stopset\nreturn: offset"
        " of the first character in string within stopset",
    )

    Strstr = Symbol(
        [0x89A70],
        [0x2089A70],
        None,
        "The strstr(3) C library function.\n\nr0: haystack\nr1: needle\nreturn: pointer"
        " into haystack where needle starts, or null pointer if no match",
    )

    Wcslen = Symbol(
        [0x8B3E8],
        [0x208B3E8],
        None,
        "The wcslen(3) C library function.\n\nr0: ws\nreturn: length of ws",
    )

    AddFloat = Symbol(
        [0x8ECB8],
        [0x208ECB8],
        None,
        "This appears to be the libgcc implementation of __addsf3 (not sure which gcc"
        " version), which implements the addition operator for IEEE 754 floating-point"
        " numbers.\n\nr0: a\nr1: b\nreturn: a + b",
    )

    DivideFloat = Symbol(
        [0x8F234],
        [0x208F234],
        None,
        "This appears to be the libgcc implementation of __divsf3 (not sure which gcc"
        " version), which implements the division operator for IEEE 754 floating-point"
        " numbers.\n\nr0: dividend\nr1: divisor\nreturn: dividend / divisor",
    )

    FloatToDouble = Symbol(
        [0x8F5EC],
        [0x208F5EC],
        None,
        "This appears to be the libgcc implementation of __extendsfdf2 (not sure which"
        " gcc version), which implements the float to double cast operation for IEEE"
        " 754 floating-point numbers.\n\nr0: float\nreturn: (double)float",
    )

    FloatToInt = Symbol(
        [0x8F670],
        [0x208F670],
        None,
        "This appears to be the libgcc implementation of __fixsfsi (not sure which gcc"
        " version), which implements the float to int cast operation for IEEE 754"
        " floating-point numbers. The output saturates if the input is out of the"
        " representable range for the int type.\n\nr0: float\nreturn: (int)float",
    )

    IntToFloat = Symbol(
        [0x8F6A4],
        [0x208F6A4],
        None,
        "This appears to be the libgcc implementation of __floatsisf (not sure which"
        " gcc version), which implements the int to float cast operation for IEEE 754"
        " floating-point numbers.\n\nr0: int\nreturn: (float)int",
    )

    UIntToFloat = Symbol(
        [0x8F6EC],
        [0x208F6EC],
        None,
        "This appears to be the libgcc implementation of __floatunsisf (not sure which"
        " gcc version), which implements the unsigned int to float cast operation for"
        " IEEE 754 floating-point numbers.\n\nr0: uint\nreturn: (float)uint",
    )

    MultiplyFloat = Symbol(
        [0x8F734],
        [0x208F734],
        None,
        "This appears to be the libgcc implementation of __mulsf3 (not sure which gcc"
        " version), which implements the multiplication operator for IEEE 754"
        " floating-point numbers.",
    )

    Sqrtf = Symbol(
        [0x8F914],
        [0x208F914],
        None,
        "The sqrtf(3) C library function.\n\nr0: x\nreturn: sqrt(x)",
    )

    SubtractFloat = Symbol(
        [0x8FA04],
        [0x208FA04],
        None,
        "This appears to be the libgcc implementation of __subsf3 (not sure which gcc"
        " version), which implements the subtraction operator for IEEE 754"
        " floating-point numbers.\n\nr0: a\nr1: b\nreturn: a - b",
    )

    DivideInt = Symbol(
        [0x8FEA4],
        [0x208FEA4],
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
        [0x900B0],
        [0x20900B0],
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
        [0x900B8],
        [0x20900B8],
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


class NaArm9Data:
    JUICE_BAR_NECTAR_IQ_GAIN = Symbol(
        [0x11810], [0x2011810], 0x1, "IQ gain when ingesting nectar at the Juice Bar."
    )

    TEXT_SPEED = Symbol([0x20C98], [0x2020C98], None, "Controls text speed.")

    HERO_START_LEVEL = Symbol(
        [0x48880], [0x2048880], None, "Starting level of the hero."
    )

    PARTNER_START_LEVEL = Symbol(
        [0x488F0], [0x20488F0], None, "Starting level of the partner."
    )

    DEFAULT_MEMORY_ARENA_SIZE = Symbol(
        [0xE58],
        [0x2000E58],
        0x4,
        "Length in bytes of the default memory allocation arena, 1991680.",
    )

    AURA_BOW_ID_LAST = Symbol(
        [0xCC34], [0x200CC34], 0x4, "Highest item ID of the aura bows."
    )

    NUMBER_OF_ITEMS = Symbol([0xE860], [0x200E860], 0x4, "Number of items in the game.")

    MAX_MONEY_CARRIED = Symbol(
        [0xED50],
        [0x200ED50],
        0x4,
        "Maximum amount of money the player can carry, 99999.",
    )

    MAX_MONEY_STORED = Symbol(
        [0x10750],
        [0x2010750],
        0x4,
        "Maximum amount of money the player can store in the Duskull Bank, 9999999.",
    )

    SCRIPT_VARS_VALUES_PTR = Symbol(
        [0x4B2F8, 0x4B4E4, 0x4C42C, 0x4C484],
        [0x204B2F8, 0x204B4E4, 0x204C42C, 0x204C484],
        0x4,
        "Hard-coded pointer to SCRIPT_VARS_VALUES.",
    )

    MONSTER_ID_LIMIT = Symbol(
        [0x5449C],
        [0x205449C],
        0x4,
        "One more than the maximum valid monster ID (0x483).",
    )

    MAX_RECRUITABLE_TEAM_MEMBERS = Symbol(
        [0x55238, 0x5564C],
        [0x2055238, 0x205564C],
        None,
        "555, appears to be the maximum number of members recruited to an exploration"
        " team, at least for the purposes of some checks that need to iterate over all"
        " team members.",
    )

    CART_REMOVED_IMG_DATA = Symbol([0x92AE8], [0x2092AE8], 0x4000, "")

    EXCLUSIVE_ITEM_STAT_BOOST_DATA = Symbol(
        [0x980E8],
        [0x20980E8],
        0x3C,
        "Contains stat boost effects for different exclusive item classes.\n\nEach"
        " 4-byte entry contains the boost data for (attack, special attack, defense,"
        " special defense), 1 byte each, for a specific exclusive item class, indexed"
        " according to the stat boost data index list.",
    )

    EXCLUSIVE_ITEM_ATTACK_BOOSTS = Symbol(
        [0x980E8], [0x20980E8], 0x39, "EXCLUSIVE_ITEM_STAT_BOOST_DATA, offset by 0"
    )

    EXCLUSIVE_ITEM_SPECIAL_ATTACK_BOOSTS = Symbol(
        [0x980E9], [0x20980E9], 0x39, "EXCLUSIVE_ITEM_STAT_BOOST_DATA, offset by 1"
    )

    EXCLUSIVE_ITEM_DEFENSE_BOOSTS = Symbol(
        [0x980EA], [0x20980EA], 0x39, "EXCLUSIVE_ITEM_STAT_BOOST_DATA, offset by 2"
    )

    EXCLUSIVE_ITEM_SPECIAL_DEFENSE_BOOSTS = Symbol(
        [0x980EB], [0x20980EB], 0x39, "EXCLUSIVE_ITEM_STAT_BOOST_DATA, offset by 3"
    )

    EXCLUSIVE_ITEM_EFFECT_DATA = Symbol(
        [0x98124],
        [0x2098124],
        0x778,
        "Contains special effects for each exclusive item.\n\nEach entry is 2 bytes,"
        " with the first entry corresponding to the first exclusive item (Prism Ruff)."
        " The first byte is the exclusive item effect ID, and the second byte is an"
        " index into other data tables (related to the more generic stat boosting"
        " effects for specific monsters).",
    )

    EXCLUSIVE_ITEM_STAT_BOOST_DATA_INDEXES = Symbol(
        [0x98125], [0x2098125], 0x777, "EXCLUSIVE_ITEM_EFFECT_DATA, offset by 1"
    )

    RECOIL_MOVE_LIST = Symbol(
        [0x98D74],
        [0x2098D74],
        0x16,
        "Null-terminated list of all the recoil moves, as 2-byte move IDs.\n\ntype:"
        " struct move_id_16[11]",
    )

    PUNCH_MOVE_LIST = Symbol(
        [0x98D8A],
        [0x2098D8A],
        0x20,
        "Null-terminated list of all the punch moves, as 2-byte move IDs.\n\ntype:"
        " struct move_id_16[16]",
    )

    SCRIPT_VARS_LOCALS = Symbol(
        [0x9CECC],
        [0x209CECC],
        0x40,
        "List of special 'local' variables available to the script engine. There are 4"
        " 16-byte entries.\n\nEach entry has the same structure as an entry in"
        " SCRIPT_VARS.\n\ntype: struct script_local_var_table",
    )

    SCRIPT_VARS = Symbol(
        [0x9D870],
        [0x209D870],
        0x730,
        "List of predefined global variables that track game state, which are available"
        " to the script engine. There are 115 16-byte entries.\n\nThese variables"
        " underpin the various ExplorerScript global variables you can use in the"
        " SkyTemple SSB debugger.\n\ntype: struct script_var_table",
    )

    DUNGEON_DATA_LIST = Symbol(
        [0x9E3A0],
        [0x209E3A0],
        0x2D0,
        "Data about every dungeon in the game.\n\nThis is an array of 180 dungeon data"
        " list entry structs. Each entry is 4 bytes, and contains floor count"
        " information along with an index into the bulk of the dungeon's data in"
        " mappa_s.bin.\n\nSee the struct definitions and End45's dungeon data document"
        " for more info.\n\ntype: struct dungeon_data_list_entry[180]",
    )

    DUNGEON_RESTRICTIONS = Symbol(
        [0xA0C64],
        [0x20A0C64],
        0xC00,
        "Data related to dungeon restrictions for every dungeon in the game.\n\nThis is"
        " an array of 256 dungeon restriction structs. Each entry is 12 bytes, and"
        " contains information about restrictions within the given dungeon.\n\nSee the"
        " struct definitions and End45's dungeon data document for more info.\n\ntype:"
        " struct dungeon_restriction[256]",
    )

    SPECIAL_BAND_STAT_BOOST = Symbol(
        [0xA186C], [0x20A186C], 0x2, "Stat boost value for the Special Band."
    )

    MUNCH_BELT_STAT_BOOST = Symbol(
        [0xA187C], [0x20A187C], 0x2, "Stat boost value for the Munch Belt."
    )

    GUMMI_STAT_BOOST = Symbol(
        [0xA1888],
        [0x20A1888],
        0x2,
        "Stat boost value if a stat boost occurs when eating normal Gummis.",
    )

    MIN_IQ_EXCLUSIVE_MOVE_USER = Symbol([0xA188C], [0x20A188C], 0x4, "")

    WONDER_GUMMI_IQ_GAIN = Symbol(
        [0xA1890], [0x20A1890], 0x2, "IQ gain when ingesting wonder gummis."
    )

    AURA_BOW_STAT_BOOST = Symbol(
        [0xA1898], [0x20A1898], 0x2, "Stat boost value for the aura bows."
    )

    MIN_IQ_ITEM_MASTER = Symbol([0xA18A4], [0x20A18A4], 0x4, "")

    DEF_SCARF_STAT_BOOST = Symbol(
        [0xA18A8], [0x20A18A8], 0x2, "Stat boost value for the Defense Scarf."
    )

    POWER_BAND_STAT_BOOST = Symbol(
        [0xA18AC], [0x20A18AC], 0x2, "Stat boost value for the Power Band."
    )

    WONDER_GUMMI_STAT_BOOST = Symbol(
        [0xA18B0],
        [0x20A18B0],
        0x2,
        "Stat boost value if a stat boost occurs when eating Wonder Gummis.",
    )

    ZINC_BAND_STAT_BOOST = Symbol(
        [0xA18B4], [0x20A18B4], 0x2, "Stat boost value for the Zinc Band."
    )

    TACTICS_UNLOCK_LEVEL_TABLE = Symbol([0xA1940], [0x20A1940], 0x18, "")

    OUTLAW_LEVEL_TABLE = Symbol(
        [0xA1998],
        [0x20A1998],
        0x20,
        "Table of 2-byte outlaw levels for outlaw missions, indexed by mission rank.",
    )

    OUTLAW_MINION_LEVEL_TABLE = Symbol(
        [0xA19B8],
        [0x20A19B8],
        0x20,
        "Table of 2-byte outlaw minion levels for outlaw hideout missions, indexed by"
        " mission rank.",
    )

    IQ_SKILL_RESTRICTIONS = Symbol(
        [0xA1A5C],
        [0x20A1A5C],
        0x8A,
        "Table of 2-byte values for each IQ skill that represent a group. IQ skills in"
        " the same group can not be enabled at the same time.",
    )

    SECONDARY_TERRAIN_TYPES = Symbol(
        [0xA1AE8],
        [0x20A1AE8],
        0xC8,
        "The type of secondary terrain for each dungeon in the game.\n\nThis is an"
        " array of 200 bytes. Each byte is an enum corresponding to one"
        " dungeon.\n\ntype: struct secondary_terrain_type_8[200]",
    )

    SENTRY_MINIGAME_DATA = Symbol([0xA1BB0], [0x20A1BB0], None, "")

    IQ_SKILLS = Symbol(
        [0xA1C7C],
        [0x20A1C7C],
        0x114,
        "Table of 4-byte values for each IQ skill that represent the required IQ value"
        " to unlock a skill.",
    )

    IQ_GROUP_SKILLS = Symbol([0xA1D90], [0x20A1D90], 0x190, "")

    IQ_GUMMI_GAIN_TABLE = Symbol([0xA22B0], [0x20A22B0], 0x288, "")

    GUMMI_BELLY_RESTORE_TABLE = Symbol([0xA2538], [0x20A2538], 0x288, "")

    BAG_CAPACITY_TABLE = Symbol(
        [0xA27D4],
        [0x20A27D4],
        0x20,
        "Array of 4-byte integers containing the bag capacity for each bag level.",
    )

    SPECIAL_EPISODE_MAIN_CHARACTERS = Symbol([0xA27F4], [0x20A27F4], 0xC8, "")

    GUEST_MONSTER_DATA = Symbol(
        [0xA28BC],
        [0x20A28BC],
        0x288,
        "Data for guest monsters that join you during certain story dungeons.\n\nArray"
        " of 18 36-byte entries.\n\nSee the struct definitions and End45's dungeon data"
        " document for more info.\n\ntype: struct guest_monster[18]",
    )

    RANK_UP_TABLE = Symbol([0xA2B44], [0x20A2B44], 0xD0, "")

    MONSTER_SPRITE_DATA = Symbol([0xA2D08], [0x20A2D08], 0x4B0, "")

    MISSION_DUNGEON_UNLOCK_TABLE = Symbol([0xA3CAC], [0x20A3CAC], None, "")

    EVENTS = Symbol(
        [0xA5488],
        [0x20A5488],
        0x1434,
        "Table of levels for the script engine, in which scenes can take place. There"
        " are a version-dependent number of 12-byte entries.\n\ntype: struct"
        " script_level[length / 12]",
    )

    ENTITIES = Symbol(
        [0xA7FF0],
        [0x20A7FF0],
        0x1218,
        "Table of entities for the script engine, which can move around and do things"
        " within a scene. There are 386 12-byte entries.\n\ntype: struct"
        " script_entity[386]",
    )

    MAP_MARKER_PLACEMENTS = Symbol(
        [0xA94D0],
        [0x20A94D0],
        0x9B0,
        "The map marker position of each dungeon on the Wonder Map.\n\nThis is an array"
        " of 310 map marker structs. Each entry is 8 bytes, and contains positional"
        " information about a dungeon on the map.\n\nSee the struct definitions and"
        " End45's dungeon data document for more info.\n\ntype: struct map_marker[310]",
    )

    MEMORY_ALLOCATION_ARENA_GETTERS = Symbol(
        [0xAEF00],
        [0x20AEF00],
        0x8,
        "Functions to get the desired memory arena for allocating and freeing heap"
        " memory.\n\ntype: struct mem_arena_getters",
    )

    PRNG_SEQUENCE_NUM = Symbol(
        [0xAEF2C],
        [0x20AEF2C],
        0x2,
        "[Runtime] The current PRNG sequence number for the general-purpose PRNG. See"
        " Rand16Bit for more information on how the general-purpose PRNG works.",
    )

    LOADED_OVERLAY_GROUP_0 = Symbol(
        [0xAF230],
        [0x20AF230],
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
        [0xAF234],
        [0x20AF234],
        0x4,
        "[Runtime] The overlay group ID of the overlay currently loaded in slot 1. A"
        " group ID of 0 denotes no overlay.\n\nOverlay group IDs that can be loaded in"
        " slot 1:\n- 0x4 (overlay 1)\n- 0x5 (overlay 2)\n- 0xD (overlay 11)\n- 0xE"
        " (overlay 29)\n- 0xF (overlay 34)\n\ntype: enum overlay_group_id",
    )

    LOADED_OVERLAY_GROUP_2 = Symbol(
        [0xAF238],
        [0x20AF238],
        0x4,
        "[Runtime] The overlay group ID of the overlay currently loaded in slot 2. A"
        " group ID of 0 denotes no overlay.\n\nOverlay group IDs that can be loaded in"
        " slot 2:\n- 0x1 (overlay 0)\n- 0x2 (overlay 10)\n- 0x3 (overlay 35)\n\ntype:"
        " enum overlay_group_id",
    )

    PACK_FILE_OPENED = Symbol(
        None,
        None,
        None,
        "[Runtime] A pointer to the 6 opened Pack files (listed at"
        " PACK_FILE_PATHS_TABLE)\n\ntype: struct pack_file_opened*",
    )

    PACK_FILE_PATHS_TABLE = Symbol(
        [0xAF6A0],
        [0x20AF6A0],
        0x18,
        "List of pointers to path strings to all known pack files.\nThe game uses this"
        " table to load its resources when launching dungeon mode.\n\ntype: char*[6]",
    )

    GAME_STATE_VALUES = Symbol([0xAF6B8], [0x20AF6B8], None, "[Runtime]")

    DUNGEON_MOVE_TABLES = Symbol(
        [0xAF6DC],
        [0x20AF6DC],
        None,
        "[Runtime] Seems to be some sort of region (a table of tables?) that holds"
        " pointers to various important tables related to moves.",
    )

    MOVE_DATA_TABLE_PTR = Symbol(
        [0xAF6E4],
        [0x20AF6E4],
        0x4,
        "[Runtime] Points to the contents of the move data table loaded from"
        " waza_p.bin\n\ntype: struct move_data_table*",
    )

    LANGUAGE_INFO_DATA = Symbol([0xAFCE8], [0x20AFCE8], None, "[Runtime]")

    NOTIFY_NOTE = Symbol(
        [0xAFEF8],
        [0x20AFEF8],
        None,
        "[Runtime] Flag related to saving and loading state?\n\ntype: bool",
    )

    DEFAULT_HERO_ID = Symbol(
        [0xAFEFC],
        [0x20AFEFC],
        0x2,
        "The default monster ID for the hero (0x4: Charmander)\n\ntype: struct"
        " monster_id_16",
    )

    DEFAULT_PARTNER_ID = Symbol(
        [0xAFEFE],
        [0x20AFEFE],
        0x2,
        "The default monster ID for the partner (0x1: Bulbasaur)\n\ntype: struct"
        " monster_id_16",
    )

    GAME_MODE = Symbol([0xAFF70], [0x20AFF70], None, "[Runtime]\n\ntype: uint8_t")

    ADVENTURE_LOG_PTR = Symbol(
        [0xAFF78], [0x20AFF78], 0x4, "[Runtime]\n\ntype: struct adventure_log*"
    )

    ITEM_TABLES_PTRS_1 = Symbol([0xB0948], [0x20B0948], 0x68, "")

    SMD_EVENTS_FUN_TABLE = Symbol([0xB0B90], [0x20B0B90], 0x1FC, "")


class NaArm9Section:
    name = "arm9"
    description = (
        "Hard-coded immediate values (literals) in instructions within the ARM 9"
        " binary."
    )
    loadaddress = 0x2000000
    length = 0xB73F8
    functions = NaArm9Functions
    data = NaArm9Data


class NaOverlay0Functions:
    pass


class NaOverlay0Data:
    TOP_MENU_MUSIC_ID = Symbol(
        [0x1720], [0x22BE1A0], None, "Music ID to play in the top menu."
    )


class NaOverlay0Section:
    name = "overlay0"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 0."
    )
    loadaddress = 0x22BCA80
    length = 0x609A0
    functions = NaOverlay0Functions
    data = NaOverlay0Data


class NaOverlay10Functions:
    SprintfStatic = Symbol(
        [0x9CC, 0x4DBC],
        [0x22BD44C, 0x22C183C],
        None,
        "Statically defined copy of sprintf(3) in overlay 10. See arm9.yml for more"
        " information.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )


class NaOverlay10Data:
    FIRST_DUNGEON_WITH_MONSTER_HOUSE_TRAPS = Symbol(
        [0x798C],
        [0x22C440C],
        0x1,
        "The first dungeon that can have extra traps spawn in Monster Houses, Dark"
        " Hill\n\ntype: struct dungeon_id_8",
    )

    BAD_POISON_DAMAGE_COOLDOWN = Symbol(
        [0x7994],
        [0x22C4414],
        0x2,
        "The number of turns between passive bad poison (toxic) damage.",
    )

    PROTEIN_STAT_BOOST = Symbol(
        [0x79A0],
        [0x22C4420],
        0x2,
        "The permanent attack boost from ingesting a Protein.",
    )

    SPAWN_CAP_NO_MONSTER_HOUSE = Symbol(
        [0x79B0],
        [0x22C4430],
        None,
        "The maximum number of enemies that can spawn on a floor without a monster"
        " house (15).",
    )

    OREN_BERRY_DAMAGE = Symbol(
        [0x79B8], [0x22C4438], 0x2, "Damage dealt by eating an Oren Berry."
    )

    SITRUS_BERRY_HP_RESTORATION = Symbol(
        [0x79F8],
        [0x22C4478],
        0x2,
        "The amount of HP restored by eating a Sitrus Berry.",
    )

    EXP_ELITE_EXP_BOOST = Symbol(
        [0x7A28],
        [0x22C44A8],
        0x2,
        "The percentage increase in experience from the Exp. Elite IQ skill",
    )

    MONSTER_HOUSE_MAX_NON_MONSTER_SPAWNS = Symbol(
        [0x7A2C],
        [0x22C44AC],
        0x2,
        "The maximum number of extra non-monster spawns (items/traps) in a Monster"
        " House, 7",
    )

    GOLD_THORN_POWER = Symbol(
        [0x7A50], [0x22C44D0], 0x2, "Attack power for Golden Thorns."
    )

    SPAWN_COOLDOWN = Symbol(
        [0x7A5C],
        [0x22C44DC],
        0x2,
        "The number of turns between enemy spawns under normal conditions.",
    )

    ORAN_BERRY_FULL_HP_BOOST = Symbol(
        [0x7A74],
        [0x22C44F4],
        0x2,
        "The permanent HP boost from eating an Oran Berry at full HP (0).",
    )

    LIFE_SEED_HP_BOOST = Symbol(
        [0x7A78], [0x22C44F8], 0x2, "The permanent HP boost from eating a Life Seed."
    )

    EXCLUSIVE_ITEM_EXP_BOOST = Symbol(
        [0x7B0C],
        [0x22C458C],
        0x2,
        "The percentage increase in experience from exp-boosting exclusive items",
    )

    INTIMIDATOR_ACTIVATION_CHANCE = Symbol(
        [0x7B38],
        [0x22C45B8],
        0x2,
        "The percentage chance that Intimidator will activate.",
    )

    ORAN_BERRY_HP_RESTORATION = Symbol(
        [0x7B6C], [0x22C45EC], 0x2, "The amount of HP restored by eating a Oran Berry."
    )

    SITRUS_BERRY_FULL_HP_BOOST = Symbol(
        [0x7B74],
        [0x22C45F4],
        0x2,
        "The permanent HP boost from eating a Sitrus Berry at full HP.",
    )

    BURN_DAMAGE_COOLDOWN = Symbol(
        [0x7B90], [0x22C4610], 0x2, "The number of turns between passive burn damage."
    )

    STICK_POWER = Symbol([0x7BA4], [0x22C4624], 0x2, "Attack power for Sticks.")

    SPAWN_COOLDOWN_THIEF_ALERT = Symbol(
        [0x7BC0],
        [0x22C4640],
        0x2,
        "The number of turns between enemy spawns when the Thief Alert condition is"
        " active.",
    )

    MONSTER_HOUSE_MAX_MONSTER_SPAWNS = Symbol(
        [0x7BE0],
        [0x22C4660],
        0x2,
        "The maximum number of monster spawns in a Monster House, 30, but multiplied by"
        " 2/3 for some reason (so the actual maximum is 45)",
    )

    SPEED_BOOST_TURNS = Symbol(
        [0x7BEC],
        [0x22C466C],
        None,
        "Number of turns (250) after which Speed Boost will trigger and increase speed"
        " by one stage.",
    )

    MIRACLE_CHEST_EXP_BOOST = Symbol(
        [0x7C18],
        [0x22C4698],
        0x2,
        "The percentage increase in experience from the Miracle Chest item",
    )

    WONDER_CHEST_EXP_BOOST = Symbol(
        [0x7C1C],
        [0x22C469C],
        0x2,
        "The percentage increase in experience from the Wonder Chest item",
    )

    SPAWN_CAP_WITH_MONSTER_HOUSE = Symbol(
        [0x7C24],
        [0x22C46A4],
        None,
        "The maximum number of enemies that can spawn on a floor with a monster house,"
        " not counting those in the monster house (4).",
    )

    POISON_DAMAGE_COOLDOWN = Symbol(
        [0x7C28], [0x22C46A8], 0x2, "The number of turns between passive poison damage."
    )

    GEO_PEBBLE_DAMAGE = Symbol(
        [0x7C34], [0x22C46B4], 0x2, "Damage dealt by Geo Pebbles."
    )

    GRAVELEROCK_DAMAGE = Symbol(
        [0x7C38], [0x22C46B8], 0x2, "Damage dealt by Gravelerocks."
    )

    RARE_FOSSIL_DAMAGE = Symbol(
        [0x7C3C], [0x22C46BC], 0x2, "Damage dealt by Rare Fossils."
    )

    GINSENG_CHANCE_3 = Symbol(
        [0x7C40],
        [0x22C46C0],
        0x2,
        "The percentage chance for...something to be set to 3 in a calculation related"
        " to the Ginseng boost.",
    )

    ZINC_STAT_BOOST = Symbol(
        [0x7C44],
        [0x22C46C4],
        0x2,
        "The permanent special defense boost from ingesting a Zinc.",
    )

    IRON_STAT_BOOST = Symbol(
        [0x7C48],
        [0x22C46C8],
        0x2,
        "The permanent defense boost from ingesting an Iron.",
    )

    CALCIUM_STAT_BOOST = Symbol(
        [0x7C4C],
        [0x22C46CC],
        0x2,
        "The permanent special attack boost from ingesting a Calcium.",
    )

    CORSOLA_TWIG_POWER = Symbol(
        [0x7C58], [0x22C46D8], 0x2, "Attack power for Corsola Twigs."
    )

    CACNEA_SPIKE_POWER = Symbol(
        [0x7C5C], [0x22C46DC], 0x2, "Attack power for Cacnea Spikes."
    )

    GOLD_FANG_POWER = Symbol([0x7C60], [0x22C46E0], 0x2, "Attack power for Gold Fangs.")

    SILVER_SPIKE_POWER = Symbol(
        [0x7C64], [0x22C46E4], 0x2, "Attack power for Silver Spikes."
    )

    IRON_THORN_POWER = Symbol(
        [0x7C68], [0x22C46E8], 0x2, "Attack power for Iron Thorns."
    )

    SLEEP_DURATION_RANGE = Symbol(
        [0x7CA0],
        [0x22C4720],
        0x4,
        "Appears to control the range of turns for which the sleep condition can"
        " last.\n\nThe first two bytes are the low value of the range, and the later"
        " two bytes are the high value.",
    )

    POWER_PITCHER_DAMAGE_MULTIPLIER = Symbol(
        [0x7D78],
        [0x22C47F8],
        0x4,
        "The multiplier for projectile damage from Power Pitcher (1.5), as a binary"
        " fixed-point number (8 fraction bits)",
    )

    AIR_BLADE_DAMAGE_MULTIPLIER = Symbol(
        [0x7DC4],
        [0x22C4844],
        None,
        "The multiplier for damage from the Air Blade (1.5), as a binary fixed-point"
        " number (8 fraction bits)",
    )

    SPEED_BOOST_DURATION_RANGE = Symbol(
        [0x7E08],
        [0x22C4888],
        0x4,
        "Appears to control the range of turns for which a speed boost can last.\n\nThe"
        " first two bytes are the low value of the range, and the later two bytes are"
        " the high value.",
    )

    OFFENSIVE_STAT_STAGE_MULTIPLIERS = Symbol(
        [0x8318],
        [0x22C4D98],
        0x54,
        "Table of multipliers for offensive stats (attack/special attack) for each"
        " stage 0-20, as binary fixed-point numbers (8 fraction bits)",
    )

    DEFENSIVE_STAT_STAGE_MULTIPLIERS = Symbol(
        [0x836C],
        [0x22C4DEC],
        0x54,
        "Table of multipliers for defensive stats (defense/special defense) for each"
        " stage 0-20, as binary fixed-point numbers (8 fraction bits)",
    )

    RANDOM_MUSIC_ID_TABLE = Symbol(
        [0x877C],
        [0x22C51FC],
        0xF0,
        "Table of music IDs for dungeons with a random assortment of music"
        " tracks.\n\nThis is a table with 30 rows, each with 4 2-byte music IDs. Each"
        " row contains the possible music IDs for a given group, from which the music"
        " track will be selected randomly.\n\ntype: struct music_id_16[30][4]",
    )

    MALE_ACCURACY_STAGE_MULTIPLIERS = Symbol(
        [0x898C],
        [0x22C540C],
        0x54,
        "Table of multipliers for the accuracy stat for males for each stage 0-20, as"
        " binary fixed-point numbers (8 fraction bits)",
    )

    MALE_EVASION_STAGE_MULTIPLIERS = Symbol(
        [0x89E0],
        [0x22C5460],
        0x54,
        "Table of multipliers for the evasion stat for males for each stage 0-20, as"
        " binary fixed-point numbers (8 fraction bits)",
    )

    FEMALE_ACCURACY_STAGE_MULTIPLIERS = Symbol(
        [0x8A34],
        [0x22C54B4],
        0x54,
        "Table of multipliers for the accuracy stat for females for each stage 0-20, as"
        " binary fixed-point numbers (8 fraction bits)",
    )

    FEMALE_EVASION_STAGE_MULTIPLIERS = Symbol(
        [0x8A88],
        [0x22C5508],
        0x54,
        "Table of multipliers for the evasion stat for females for each stage 0-20, as"
        " binary fixed-point numbers (8 fraction bits)",
    )

    MUSIC_ID_TABLE = Symbol(
        [0x8ADC],
        [0x22C555C],
        0x154,
        "List of music IDs used in dungeons with a single music track.\n\nThis is an"
        " array of 170 2-byte music IDs, and is indexed into by the music value in the"
        " floor properties struct for a given floor. Music IDs with the highest bit set"
        " (0x8000) are indexes into the RANDOM_MUSIC_ID_TABLE.\n\ntype: struct"
        " music_id_16[170] (or not a music ID if the highest bit is set)",
    )

    TYPE_MATCHUP_TABLE = Symbol(
        [0x8C30],
        [0x22C56B0],
        0x288,
        "Table of type matchups.\n\nEach row corresponds to the type matchups of a"
        " specific attack type, with each entry within the row specifying the type's"
        " effectiveness against a target type.\n\ntype: struct type_matchup_table",
    )

    FIXED_ROOM_MONSTER_SPAWN_STATS_TABLE = Symbol(
        [0x8EB8],
        [0x22C5938],
        0x4A4,
        "Table of stats for monsters that can spawn in fixed rooms, pointed into by the"
        " FIXED_ROOM_MONSTER_SPAWN_TABLE.\n\nThis is an array of 99 12-byte entries"
        " containing stat spreads for one monster entry each.\n\ntype: struct"
        " fixed_room_monster_spawn_stats_entry[99]",
    )

    TILESET_PROPERTIES = Symbol([0x989C], [0x22C631C], 0x954, "")

    FIXED_ROOM_PROPERTIES_TABLE = Symbol(
        [0xA1F0],
        [0x22C6C70],
        0xC00,
        "Table of properties for fixed rooms.\n\nThis is an array of 256 12-byte"
        " entries containing properties for a given fixed room ID.\n\nSee the struct"
        " definitions and End45's dungeon data document for more info.\n\ntype: struct"
        " fixed_room_properties_entry[256]",
    )

    MOVE_ANIMATION_INFO = Symbol([0xC5E4], [0x22C9064], None, "")


class NaOverlay10Section:
    name = "overlay10"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 10."
    )
    loadaddress = 0x22BCA80
    length = 0x1F7A0
    functions = NaOverlay10Functions
    data = NaOverlay10Data


class NaOverlay34Functions:
    pass


class NaOverlay34Data:
    UNKNOWN_MENU_CONFIRM = Symbol([0xDE4], [0x22DD024], 0x18, "")

    DUNGEON_DEBUG_MENU = Symbol([0xE0C], [0x22DD04C], 0x28, "")


class NaOverlay34Section:
    name = "overlay34"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 34."
    )
    loadaddress = 0x22DC240
    length = 0xE60
    functions = NaOverlay34Functions
    data = NaOverlay34Data


class NaOverlay1Functions:
    pass


class NaOverlay1Data:
    CONTINUE_CHOICE = Symbol([0x12048], [0x233B568], 0x20, "")

    SUBMENU = Symbol([0x12068], [0x233B588], 0x48, "")

    MAIN_MENU = Symbol([0x120B0], [0x233B5D0], 0xA0, "")

    MAIN_MENU_CONFIRM = Symbol([0x1222C], [0x233B74C], 0x18, "")

    MAIN_DEBUG_MENU_1 = Symbol([0x122F0], [0x233B810], 0x60, "")

    MAIN_DEBUG_MENU_2 = Symbol([0x12370], [0x233B890], 0x38, "")


class NaOverlay1Section:
    name = "overlay1"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 1."
    )
    loadaddress = 0x2329520
    length = 0x12D20
    functions = NaOverlay1Functions
    data = NaOverlay1Data


class NaOverlay4Functions:
    pass


class NaOverlay4Data:
    pass


class NaOverlay4Section:
    name = "overlay4"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 4."
    )
    loadaddress = 0x233CA80
    length = 0x2BE0
    functions = NaOverlay4Functions
    data = NaOverlay4Data


class NaOverlay6Functions:
    pass


class NaOverlay6Data:
    pass


class NaOverlay6Section:
    name = "overlay6"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 6."
    )
    loadaddress = 0x233CA80
    length = 0x2460
    functions = NaOverlay6Functions
    data = NaOverlay6Data


class NaOverlay7Functions:
    pass


class NaOverlay7Data:
    pass


class NaOverlay7Section:
    name = "overlay7"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 7."
    )
    loadaddress = 0x233CA80
    length = 0x5100
    functions = NaOverlay7Functions
    data = NaOverlay7Data


class NaOverlay9Functions:
    pass


class NaOverlay9Data:
    TOP_MENU_RETURN_MUSIC_ID = Symbol(
        [0xE80],
        [0x233D900],
        None,
        "Song playing in the main menu when returning from the Sky Jukebox.",
    )


class NaOverlay9Section:
    name = "overlay9"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 9."
    )
    loadaddress = 0x233CA80
    length = 0x2D80
    functions = NaOverlay9Functions
    data = NaOverlay9Data


class NaOverlay30Functions:
    pass


class NaOverlay30Data:
    pass


class NaOverlay30Section:
    name = "overlay30"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 30."
    )
    loadaddress = 0x2382820
    length = 0x38A0
    functions = NaOverlay30Functions
    data = NaOverlay30Data


class NaOverlay31Functions:
    pass


class NaOverlay31Data:
    DUNGEON_MAIN_MENU = Symbol([0x75B4], [0x2389DD4], 0x40, "")

    DUNGEON_SUBMENU_1 = Symbol([0x7650], [0x2389E70], 0x20, "")

    DUNGEON_SUBMENU_2 = Symbol([0x7670], [0x2389E90], 0x20, "")

    DUNGEON_SUBMENU_3 = Symbol([0x7690], [0x2389EB0], 0x20, "")

    DUNGEON_SUBMENU_4 = Symbol([0x76B0], [0x2389ED0], 0x20, "")

    DUNGEON_SUBMENU_5 = Symbol([0x78FC], [0x238A11C], 0x18, "")

    DUNGEON_SUBMENU_6 = Symbol([0x7980], [0x238A1A0], 0x48, "")


class NaOverlay31Section:
    name = "overlay31"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 31."
    )
    loadaddress = 0x2382820
    length = 0x7A80
    functions = NaOverlay31Functions
    data = NaOverlay31Data


class NaOverlay13Functions:
    pass


class NaOverlay13Data:
    STARTERS_PARTNER_IDS = Symbol(
        [0x1F4C], [0x238C08C], 0x2A, "type: struct monster_id_16[21]"
    )

    STARTERS_HERO_IDS = Symbol(
        [0x1F78], [0x238C0B8], 0x40, "type: struct monster_id_16[32]"
    )

    STARTERS_STRINGS = Symbol([0x200C], [0x238C14C], 0x60, "")

    QUIZ_QUESTION_STRINGS = Symbol([0x206C], [0x238C1AC], 0x84, "")

    QUIZ_ANSWER_STRINGS = Symbol([0x20F0], [0x238C230], 0x160, "")

    UNKNOWN_MENU_1 = Symbol([0x2D8C], [0x238CECC], 0x48, "")


class NaOverlay13Section:
    name = "overlay13"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 13."
    )
    loadaddress = 0x238A140
    length = 0x2E80
    functions = NaOverlay13Functions
    data = NaOverlay13Data


class NaOverlay14Functions:
    pass


class NaOverlay14Data:
    FOOTPRINT_DEBUG_MENU = Symbol([0x3960], [0x238DAA0], 0x48, "")


class NaOverlay14Section:
    name = "overlay14"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 14."
    )
    loadaddress = 0x238A140
    length = 0x3AE0
    functions = NaOverlay14Functions
    data = NaOverlay14Data


class NaOverlay15Functions:
    pass


class NaOverlay15Data:
    BANK_MAIN_MENU = Symbol([0xF14], [0x238B054], 0x28, "")


class NaOverlay15Section:
    name = "overlay15"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 15."
    )
    loadaddress = 0x238A140
    length = 0x1060
    functions = NaOverlay15Functions
    data = NaOverlay15Data


class NaOverlay16Functions:
    pass


class NaOverlay16Data:
    EVO_MENU_CONFIRM = Symbol([0x2BC8], [0x238CD08], 0x18, "")

    EVO_SUBMENU = Symbol([0x2BE0], [0x238CD20], 0x20, "")

    EVO_MAIN_MENU = Symbol([0x2C00], [0x238CD40], 0x20, "")


class NaOverlay16Section:
    name = "overlay16"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 16."
    )
    loadaddress = 0x238A140
    length = 0x2D20
    functions = NaOverlay16Functions
    data = NaOverlay16Data


class NaOverlay18Functions:
    pass


class NaOverlay18Data:
    MOVES_MENU_CONFIRM = Symbol([0x31E0], [0x238D320], 0x18, "")

    MOVES_SUBMENU_1 = Symbol([0x31F8], [0x238D338], 0x20, "")

    MOVES_SUBMENU_2 = Symbol([0x3218], [0x238D358], 0x20, "")

    MOVES_MAIN_MENU = Symbol([0x3238], [0x238D378], 0x20, "")

    MOVES_SUBMENU_3 = Symbol([0x3258], [0x238D398], 0x28, "")

    MOVES_SUBMENU_4 = Symbol([0x3280], [0x238D3C0], 0x30, "")

    MOVES_SUBMENU_5 = Symbol([0x32B0], [0x238D3F0], 0x48, "")

    MOVES_SUBMENU_6 = Symbol([0x32F8], [0x238D438], 0x48, "")

    MOVES_SUBMENU_7 = Symbol([0x3340], [0x238D480], 0x48, "")


class NaOverlay18Section:
    name = "overlay18"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 18."
    )
    loadaddress = 0x238A140
    length = 0x3500
    functions = NaOverlay18Functions
    data = NaOverlay18Data


class NaOverlay21Functions:
    pass


class NaOverlay21Data:
    SWAP_SHOP_MENU_CONFIRM = Symbol([0x28F8], [0x238CA38], 0x18, "")

    SWAP_SHOP_SUBMENU_1 = Symbol([0x2910], [0x238CA50], 0x18, "")

    SWAP_SHOP_SUBMENU_2 = Symbol([0x2928], [0x238CA68], 0x20, "")

    SWAP_SHOP_MAIN_MENU_1 = Symbol([0x2948], [0x238CA88], 0x20, "")

    SWAP_SHOP_MAIN_MENU_2 = Symbol([0x2968], [0x238CAA8], 0x28, "")

    SWAP_SHOP_SUBMENU_3 = Symbol([0x2990], [0x238CAD0], 0x30, "")


class NaOverlay21Section:
    name = "overlay21"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 21."
    )
    loadaddress = 0x238A140
    length = 0x2E20
    functions = NaOverlay21Functions
    data = NaOverlay21Data


class NaOverlay22Functions:
    pass


class NaOverlay22Data:
    SHOP_MENU_CONFIRM = Symbol([0x4728], [0x238E868], 0x18, "")

    SHOP_MAIN_MENU_1 = Symbol([0x4740], [0x238E880], 0x20, "")

    SHOP_MAIN_MENU_2 = Symbol([0x4760], [0x238E8A0], 0x20, "")

    SHOP_MAIN_MENU_3 = Symbol([0x4780], [0x238E8C0], 0x30, "")


class NaOverlay22Section:
    name = "overlay22"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 22."
    )
    loadaddress = 0x238A140
    length = 0x4B40
    functions = NaOverlay22Functions
    data = NaOverlay22Data


class NaOverlay23Functions:
    pass


class NaOverlay23Data:
    STORAGE_MENU_CONFIRM = Symbol([0x31BC], [0x238D2FC], 0x18, "")

    STORAGE_MAIN_MENU_1 = Symbol([0x31D4], [0x238D314], 0x20, "")

    STORAGE_MAIN_MENU_2 = Symbol([0x31F4], [0x238D334], 0x20, "")

    STORAGE_MAIN_MENU_3 = Symbol([0x3214], [0x238D354], 0x20, "")

    STORAGE_MAIN_MENU_4 = Symbol([0x3234], [0x238D374], 0x28, "")


class NaOverlay23Section:
    name = "overlay23"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 23."
    )
    loadaddress = 0x238A140
    length = 0x3780
    functions = NaOverlay23Functions
    data = NaOverlay23Data


class NaOverlay24Functions:
    pass


class NaOverlay24Data:
    DAYCARE_MENU_CONFIRM = Symbol([0x23E0], [0x238C520], 0x18, "")

    DAYCARE_MAIN_MENU = Symbol([0x23F8], [0x238C538], 0x20, "")


class NaOverlay24Section:
    name = "overlay24"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 24."
    )
    loadaddress = 0x238A140
    length = 0x24E0
    functions = NaOverlay24Functions
    data = NaOverlay24Data


class NaOverlay26Functions:
    pass


class NaOverlay26Data:
    pass


class NaOverlay26Section:
    name = "overlay26"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 26."
    )
    loadaddress = 0x238A140
    length = 0xE40
    functions = NaOverlay26Functions
    data = NaOverlay26Data


class NaOverlay27Functions:
    pass


class NaOverlay27Data:
    DISCARD_ITEMS_MENU_CONFIRM = Symbol([0x281C], [0x238C95C], 0x18, "")

    DISCARD_ITEMS_SUBMENU_1 = Symbol([0x2834], [0x238C974], 0x20, "")

    DISCARD_ITEMS_SUBMENU_2 = Symbol([0x2854], [0x238C994], 0x20, "")

    DISCARD_ITEMS_MAIN_MENU = Symbol([0x2874], [0x238C9B4], 0x28, "")


class NaOverlay27Section:
    name = "overlay27"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 27."
    )
    loadaddress = 0x238A140
    length = 0x2D60
    functions = NaOverlay27Functions
    data = NaOverlay27Data


class NaOverlay32Functions:
    pass


class NaOverlay32Data:
    pass


class NaOverlay32Section:
    name = "overlay32"
    description = "Unused; all zeroes."
    loadaddress = 0x2382820
    length = 0x20
    functions = NaOverlay32Functions
    data = NaOverlay32Data


class NaRamFunctions:
    pass


class NaRamData:
    DUNGEON_COLORMAP_PTR = Symbol(
        [0x1B9CF4],
        [0x21B9CF4],
        0x4,
        "Pointer to a colormap used to render colors in a dungeon.\n\nThe colormap is a"
        " list of 4-byte RGB colors of the form {R, G, B, padding}, which the game"
        " indexes into when rendering colors. Some weather conditions modify the"
        " colormap, which is how the color scheme changes when it's, e.g., raining.",
    )

    DUNGEON_STRUCT = Symbol(
        [0x1B9D34],
        [0x21B9D34],
        0x2CB14,
        "The dungeon context struct used for tons of stuff in dungeon mode. See struct"
        " dungeon in the C headers.\n\nThis struct never seems to be referenced"
        " directly, and is instead usually accessed via DUNGEON_PTR in overlay"
        " 29.\n\ntype: struct dungeon",
    )

    MOVE_DATA_TABLE = Symbol(
        [0x2113CC],
        [0x22113CC],
        0x38C6,
        "The move data table loaded directly from /BALANCE/waza_p.bin. See struct"
        " move_data_table in the C headers.\n\nPointed to by MOVE_DATA_TABLE_PTR in the"
        " ARM 9 binary.\n\ntype: struct move_data_table",
    )

    FRAMES_SINCE_LAUNCH = Symbol(
        [0x2A354C, 0x2A359C],
        [0x22A354C, 0x22A359C],
        0x4,
        "Starts at 0 when the game is first launched, and continuously ticks up once"
        " per frame while the game is running.",
    )

    BAG_ITEMS = Symbol(
        [0x2A3824],
        [0x22A3824],
        0x12C,
        "Array of item structs within the player's bag.\n\nWhile the game only allows a"
        " maximum of 48 items during normal play, it seems to read up to 50 item slots"
        " if filled.\n\ntype: struct item[50]",
    )

    BAG_ITEMS_PTR = Symbol([0x2A3BA8], [0x22A3BA8], 0x4, "Pointer to BAG_ITEMS.")

    STORAGE_ITEMS = Symbol(
        [0x2A3BAE],
        [0x22A3BAE],
        0x7D0,
        "Array of item IDs in the player's item storage.\n\nFor stackable items, the"
        " quantities are stored elsewhere, in STORAGE_ITEM_QUANTITIES.\n\ntype: struct"
        " item_id_16[1000]",
    )

    STORAGE_ITEM_QUANTITIES = Symbol(
        [0x2A437E],
        [0x22A437E],
        0x7D0,
        "Array of 1000 2-byte (unsigned) quantities corresponding to the item IDs in"
        " STORAGE_ITEMS.\n\nIf the corresponding item ID is not a stackable item, the"
        " entry in this array is unused, and will be 0.",
    )

    KECLEON_SHOP_ITEMS_PTR = Symbol(
        [0x2A4B50], [0x22A4B50], 0x4, "Pointer to KECLEON_SHOP_ITEMS."
    )

    KECLEON_SHOP_ITEMS = Symbol(
        [0x2A4B54],
        [0x22A4B54],
        0x20,
        "Array of up to 8 items in the Kecleon Shop of the form {struct item_id_16 id,"
        " uint16_t quantity}.\n\nIf there are fewer than 8 items, the array is expected"
        " to be null-terminated.",
    )

    UNUSED_KECLEON_SHOP_ITEMS = Symbol(
        [0x2A4B74],
        [0x22A4B74],
        0x20,
        "Seems to be another array like KECLEON_SHOP_ITEMS, but don't actually appear"
        " to be used by the Kecleon Shop.",
    )

    KECLEON_WARES_ITEMS_PTR = Symbol(
        [0x2A4B94], [0x22A4B94], 0x4, "Pointer to KECLEON_WARES_ITEMS."
    )

    KECLEON_WARES_ITEMS = Symbol(
        [0x2A4B98],
        [0x22A4B98],
        0x10,
        "Array of up to 4 items in Kecleon Wares of the form {struct item_id_16 id,"
        " uint16_t quantity}.\n\nIf there are fewer than 4 items, the array is expected"
        " to be null-terminated.",
    )

    UNUSED_KECLEON_WARES_ITEMS = Symbol(
        [0x2A4BA8],
        [0x22A4BA8],
        0x10,
        "Seems to be another array like KECLEON_WARES_ITEMS, but don't actually appear"
        " to be used by Kecleon Wares.",
    )

    MONEY_CARRIED = Symbol(
        [0x2A4BB8],
        [0x22A4BB8],
        0x4,
        "The amount of money the player is currently carrying.",
    )

    MONEY_STORED = Symbol(
        [0x2A4BC4],
        [0x22A4BC4],
        0x4,
        "The amount of money the player currently has stored in the Duskull Bank.",
    )

    LAST_NEW_MOVE = Symbol(
        [0x2AAE4C],
        [0x22AAE4C],
        0x8,
        "Move struct of the last new move introduced when learning a new move. Persists"
        " even after the move selection is made in the menu.\n\ntype: struct move",
    )

    SCRIPT_VARS_VALUES = Symbol(
        [0x2AB0AC],
        [0x22AB0AC],
        0x400,
        "The table of game variable values. Its structure is determined by"
        " SCRIPT_VARS.\n\nNote that with the script variable list defined in"
        " SCRIPT_VARS, the used length of this table is actually only 0x2B4. However,"
        " the real length of this table is 0x400 based on the game code.\n\ntype:"
        " struct script_var_value_table",
    )

    BAG_LEVEL = Symbol(
        [0x2AB15C],
        [0x22AB15C],
        0x1,
        "The player's bag level, which determines the bag capacity. This indexes"
        " directly into the BAG_CAPACITY_TABLE in the ARM9 binary.",
    )

    DEBUG_SPECIAL_EPISODE_NUMBER = Symbol(
        [0x2AB4AC],
        [0x22AB4AC],
        0x1,
        "The number of the special episode currently being played.\n\n0: normal,"
        " Bidoof's Wish\n1: Igglybuff the Prodigy\n2: Today's 'Oh My Gosh'\n3: Here"
        " Comes Team Charm!\n4: In the Future of Darkness",
    )

    PENDING_DUNGEON_ID = Symbol(
        [0x2AB4FC],
        [0x22AB4FC],
        0x1,
        "The ID of the selected dungeon when setting off from the"
        " overworld.\n\nControls the text and map location during the 'map cutscene'"
        " just before entering a dungeon, as well as the actual dungeon loaded"
        " afterwards.\n\ntype: struct dungeon_id_8",
    )

    PENDING_STARTING_FLOOR = Symbol(
        [0x2AB4FD],
        [0x22AB4FD],
        0x1,
        "The floor number to start from in the dungeon specified by"
        " PENDING_DUNGEON_ID.",
    )

    PLAY_TIME_SECONDS = Symbol(
        [0x2AB694], [0x22AB694], 0x4, "The player's total play time in seconds."
    )

    PLAY_TIME_FRAME_COUNTER = Symbol(
        [0x2AB698],
        [0x22AB698],
        0x1,
        "Counts from 0-59 in a loop, with the play time being incremented by 1 second"
        " with each rollover.",
    )

    TEAM_NAME = Symbol(
        [0x2AB918],
        [0x22AB918],
        0xC,
        "The team name.\n\nA null-terminated string, with a maximum length of 10."
        " Presumably encoded with the ANSI/Shift JIS encoding the game typically"
        " uses.\n\nThis is presumably part of a larger struct, together with other"
        " nearby data.",
    )

    HERO_SPECIES_ID = Symbol(
        [0x2ABDE4],
        [0x22ABDE4],
        0x2,
        "The hero's species ID.\n\nThis is presumably part of a larger struct, together"
        " with other nearby data.\n\ntype: struct monster_id_16",
    )

    HERO_NICKNAME = Symbol(
        [0x2ABE1A],
        [0x22ABE1A],
        0xA,
        "The hero's nickname.\n\nA null-terminated string, with a maximum length of 10."
        " Presumably encoded with the ANSI/Shift JIS encoding the game typically"
        " uses.\n\nThis is presumably part of a larger struct, together with other"
        " nearby data.",
    )

    PARTNER_SPECIES_ID = Symbol(
        [0x2ABE28],
        [0x22ABE28],
        0x2,
        "The partner's species ID.\n\nThis is presumably part of a larger struct,"
        " together with other nearby data.\n\ntype: struct monster_id_16",
    )

    LEADER_IQ_SKILLS = Symbol(
        [0x2B5198],
        [0x22B5198],
        0xC,
        "Unlocked IQ skills of the current leader, available for selection from the IQ"
        " skills menu.\n\nOne bit per skill (1 if unlocked). Same format as the IQ"
        " skills bitvector on the monster info struct.\n\nThis is presumably part of a"
        " larger struct, together with other nearby data.",
    )

    LEADER_NICKNAME = Symbol(
        [0x2B51AA],
        [0x22B51AA],
        0xA,
        "The current leader's nickname.\n\nA null-terminated string, with a maximum"
        " length of 10. Presumably encoded with the ANSI/Shift JIS encoding the game"
        " typically uses.\n\nThis is presumably part of a larger struct, together with"
        " other nearby data.",
    )

    PARTY_MEMBER_2_IQ_SKILLS = Symbol(
        [0x2B5200],
        [0x22B5200],
        0xC,
        "Unlocked IQ skills of the second party member, available for selection from"
        " the IQ skills menu.\n\nOne bit per skill (1 if unlocked). Same format as the"
        " IQ skills bitvector on the monster info struct.\n\nThis is presumably part of"
        " a larger struct, together with other nearby data.",
    )

    FRAMES_SINCE_LAUNCH_TIMES_THREE = Symbol(
        [0x2B99C4],
        [0x22B99C4],
        0x4,
        "Starts at 0 when the game is first launched, and ticks up by 3 per frame while"
        " the game is running.",
    )

    TURNING_ON_THE_SPOT_FLAG = Symbol(
        [0x37C9A6],
        [0x237C9A6],
        0x1,
        "[Runtime] Flag for whether the player is turning on the spot (pressing Y).",
    )

    FLOOR_GENERATION_STATUS = Symbol(
        [0x37CFBC],
        [0x237CFBC],
        0x40,
        "[Runtime] Status data related to generation of the current floor in a"
        " dungeon.\n\nThis data is populated as the dungeon floor is"
        " generated.\n\ntype: struct floor_generation_status",
    )


class NaRamSection:
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
    functions = NaRamFunctions
    data = NaRamData


class NaOverlay35Functions:
    pass


class NaOverlay35Data:
    pass


class NaOverlay35Section:
    name = "overlay35"
    description = "Unused; all zeroes."
    loadaddress = 0x22BCA80
    length = 0x20
    functions = NaOverlay35Functions
    data = NaOverlay35Data


class NaOverlay33Functions:
    pass


class NaOverlay33Data:
    pass


class NaOverlay33Section:
    name = "overlay33"
    description = "Unused; all zeroes."
    loadaddress = 0x2382820
    length = 0x20
    functions = NaOverlay33Functions
    data = NaOverlay33Data


class NaSections:
    overlay20 = NaOverlay20Section

    overlay3 = NaOverlay3Section

    overlay8 = NaOverlay8Section

    overlay5 = NaOverlay5Section

    overlay17 = NaOverlay17Section

    overlay19 = NaOverlay19Section

    overlay12 = NaOverlay12Section

    overlay2 = NaOverlay2Section

    overlay28 = NaOverlay28Section

    overlay29 = NaOverlay29Section

    overlay11 = NaOverlay11Section

    overlay25 = NaOverlay25Section

    arm9 = NaArm9Section

    overlay0 = NaOverlay0Section

    overlay10 = NaOverlay10Section

    overlay34 = NaOverlay34Section

    overlay1 = NaOverlay1Section

    overlay4 = NaOverlay4Section

    overlay6 = NaOverlay6Section

    overlay7 = NaOverlay7Section

    overlay9 = NaOverlay9Section

    overlay30 = NaOverlay30Section

    overlay31 = NaOverlay31Section

    overlay13 = NaOverlay13Section

    overlay14 = NaOverlay14Section

    overlay15 = NaOverlay15Section

    overlay16 = NaOverlay16Section

    overlay18 = NaOverlay18Section

    overlay21 = NaOverlay21Section

    overlay22 = NaOverlay22Section

    overlay23 = NaOverlay23Section

    overlay24 = NaOverlay24Section

    overlay26 = NaOverlay26Section

    overlay27 = NaOverlay27Section

    overlay32 = NaOverlay32Section

    ram = NaRamSection

    overlay35 = NaOverlay35Section

    overlay33 = NaOverlay33Section

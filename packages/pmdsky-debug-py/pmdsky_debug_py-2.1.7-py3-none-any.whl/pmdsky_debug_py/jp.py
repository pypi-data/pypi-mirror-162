from .protocol import Symbol


class JpOverlay20Functions:
    pass


class JpOverlay20Data:
    RECYCLE_MENU_CONFIRM_1 = Symbol(None, None, None, "")

    RECYCLE_MENU_CONFIRM_2 = Symbol(None, None, None, "")

    RECYCLE_SUBMENU_1 = Symbol(None, None, None, "")

    RECYCLE_SUBMENU_2 = Symbol(None, None, None, "")

    RECYCLE_MAIN_MENU_1 = Symbol(None, None, None, "")

    RECYCLE_MAIN_MENU_2 = Symbol(None, None, None, "")

    RECYCLE_MAIN_MENU_3 = Symbol(None, None, None, "")


class JpOverlay20Section:
    name = "overlay20"
    description = "Controls the Recycle Shop."
    loadaddress = 0x238B6A0
    length = 0x3000
    functions = JpOverlay20Functions
    data = JpOverlay20Data


class JpOverlay3Functions:
    pass


class JpOverlay3Data:
    pass


class JpOverlay3Section:
    name = "overlay3"
    description = "Controls the Friend Rescue submenu within the top menu."
    loadaddress = 0x233E300
    length = 0xA160
    functions = JpOverlay3Functions
    data = JpOverlay3Data


class JpOverlay8Functions:
    pass


class JpOverlay8Data:
    pass


class JpOverlay8Section:
    name = "overlay8"
    description = (
        "Controls the Send Demo Dungeon submenu within the top menu (under 'Other')."
    )
    loadaddress = 0x233E300
    length = 0x2200
    functions = JpOverlay8Functions
    data = JpOverlay8Data


class JpOverlay5Functions:
    pass


class JpOverlay5Data:
    pass


class JpOverlay5Section:
    name = "overlay5"
    description = "Controls the Trade Team submenu within the top menu."
    loadaddress = 0x233E300
    length = 0x3260
    functions = JpOverlay5Functions
    data = JpOverlay5Data


class JpOverlay17Functions:
    pass


class JpOverlay17Data:
    ASSEMBLY_MENU_CONFIRM = Symbol(None, None, None, "")

    ASSEMBLY_MAIN_MENU_1 = Symbol(None, None, None, "")

    ASSEMBLY_MAIN_MENU_2 = Symbol(None, None, None, "")

    ASSEMBLY_SUBMENU_1 = Symbol(None, None, None, "")

    ASSEMBLY_SUBMENU_2 = Symbol(None, None, None, "")

    ASSEMBLY_SUBMENU_3 = Symbol(None, None, None, "")

    ASSEMBLY_SUBMENU_4 = Symbol(None, None, None, "")

    ASSEMBLY_SUBMENU_5 = Symbol(None, None, None, "")

    ASSEMBLY_SUBMENU_6 = Symbol(None, None, None, "")

    ASSEMBLY_SUBMENU_7 = Symbol(None, None, None, "")


class JpOverlay17Section:
    name = "overlay17"
    description = "Controls the Chimecho Assembly."
    loadaddress = 0x238B6A0
    length = 0x1CE0
    functions = JpOverlay17Functions
    data = JpOverlay17Data


class JpOverlay19Functions:
    pass


class JpOverlay19Data:
    BAR_MENU_CONFIRM_1 = Symbol(None, None, None, "")

    BAR_MENU_CONFIRM_2 = Symbol(None, None, None, "")

    BAR_MAIN_MENU = Symbol(None, None, None, "")

    BAR_SUBMENU_1 = Symbol(None, None, None, "")

    BAR_SUBMENU_2 = Symbol(None, None, None, "")


class JpOverlay19Section:
    name = "overlay19"
    description = "Controls Spinda's Juice Bar."
    loadaddress = 0x238B6A0
    length = 0x4220
    functions = JpOverlay19Functions
    data = JpOverlay19Data


class JpOverlay12Functions:
    pass


class JpOverlay12Data:
    pass


class JpOverlay12Section:
    name = "overlay12"
    description = "Unused; all zeroes."
    loadaddress = 0x238B6A0
    length = 0x20
    functions = JpOverlay12Functions
    data = JpOverlay12Data


class JpOverlay2Functions:
    pass


class JpOverlay2Data:
    pass


class JpOverlay2Section:
    name = "overlay2"
    description = (
        "Controls the Nintendo WFC Settings interface, accessed from the top menu"
        " (Other > Nintendo WFC > Nintendo WFC Settings). Presumably contains code for"
        " Nintendo Wi-Fi setup."
    )
    loadaddress = 0x232ACC0
    length = 0x2AFA0
    functions = JpOverlay2Functions
    data = JpOverlay2Data


class JpOverlay28Functions:
    pass


class JpOverlay28Data:
    pass


class JpOverlay28Section:
    name = "overlay28"
    description = "Controls the staff credits sequence."
    loadaddress = 0x238B6A0
    length = 0xC60
    functions = JpOverlay28Functions
    data = JpOverlay28Data


class JpOverlay29Functions:
    DungeonAlloc = Symbol(
        [0x281C],
        [0x22E00FC],
        None,
        "Allocates a new dungeon struct.\n\nThis updates the master dungeon pointer and"
        " returns a copy of that pointer.\n\nreturn: pointer to a newly allocated"
        " dungeon struct",
    )

    GetDungeonPtrMaster = Symbol(
        None,
        None,
        None,
        "Returns the master dungeon pointer (a global, see"
        " DUNGEON_PTR_MASTER).\n\nreturn: pointer to a newly allocated dungeon struct",
    )

    DungeonZInit = Symbol(
        [0x2850],
        [0x22E0130],
        None,
        "Zero-initializes the dungeon struct pointed to by the master dungeon"
        " pointer.\n\nNo params.",
    )

    DungeonFree = Symbol(
        None,
        None,
        None,
        "Frees the dungeons struct pointer to by the master dungeon pointer, and"
        " nullifies the pointer.\n\nNo params.",
    )

    RunDungeon = Symbol(
        [0x2CF8],
        [0x22E05D8],
        None,
        "Called at the start of a dungeon. Initializes the dungeon struct from"
        " specified dungeon data. Includes a loop that does not break until the dungeon"
        " is cleared, and another one inside it that runs until the current floor"
        " ends.\n\nr0: Pointer to the struct containing info used to initialize the"
        " dungeon. See type dungeon_init for details.\nr1: Pointer to the dungeon data"
        " struct that will be used during the dungeon.",
    )

    EntityIsValid = Symbol(
        None,
        None,
        None,
        "Checks if an entity pointer points to a valid entity (not entity type 0, which"
        " represents no entity).\n\nr0: entity pointer\nreturn: bool",
    )

    GetFloorType = Symbol(
        [0x4168],
        [0x22E1A48],
        None,
        "Get the current floor type.\n\nFloor types:\n  0 appears to mean the current"
        " floor is 'normal'\n  1 appears to mean the current floor is a fixed floor\n "
        " 2 means the current floor has a rescue point\n\nreturn: floor type",
    )

    TryForcedLoss = Symbol(
        [0x43CC],
        [0x22E1CAC],
        None,
        "Attempts to trigger a forced loss of the type specified in"
        " dungeon::forced_loss_reason.\n\nr0: if true, the function will not check for"
        " the end of the floor condition and will skip other (unknown) actions in case"
        " of forced loss.\nreturn: true if the forced loss happens, false otherwise",
    )

    FixedRoomIsSubstituteRoom = Symbol(
        None,
        None,
        None,
        "Checks if the current fixed room is the 'substitute room' (ID"
        " 0x6E).\n\nreturn: bool",
    )

    StoryRestrictionsEnabled = Symbol(
        None,
        None,
        None,
        "Returns true if certain special restrictions are enabled.\n\nIf true, you will"
        " get kicked out of the dungeon if a team member that passes the"
        " arm9::JoinedAtRangeCheck2 check faints.\n\nreturn: !dungeon::nonstory_flag ||"
        " dungeon::hidden_land_flag",
    )

    FadeToBlack = Symbol(
        None,
        None,
        None,
        "Fades the screen to black across several frames.\n\nNo params.",
    )

    GetTileAtEntity = Symbol(
        [0x53D8],
        [0x22E2CB8],
        None,
        "Returns a pointer to the tile where an entity is located.\n\nr0: pointer to"
        " entity\nreturns: pointer to tile",
    )

    CanTargetEntity = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Checks if a monster can target a position. This function just calls"
        " IsPositionInSight using the position of the user as the origin.\n\nr0: Entity"
        " pointer\nr1: Target position\nreturn: True if the specified monster can"
        " target the target position, false otherwise.",
    )

    SubstitutePlaceholderStringTags = Symbol(
        [0x688C],
        [0x22E416C],
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
        None,
        None,
        None,
        "Sets the Map Surveyor flag in the dungeon struct to true if a team member has"
        " Map Surveyor, sets it to false otherwise.\n\nThis function has two variants:"
        " in the EU ROM, it will return true if the flag was changed. The NA version"
        " will return the new value of the flag instead.\n\nreturn: bool",
    )

    ItemIsActive = Symbol(
        None,
        None,
        None,
        "Checks if a monster is holding a certain item that isn't disabled by"
        " Klutz.\n\nr0: entity pointer\nr1: item ID\nreturn: bool",
    )

    UpdateStatusIconFlags = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Returns true if the specified monster is included in the floor's monster spawn"
        " list (the modified list after a maximum of 14 different species were chosen,"
        " not the raw list read from the mappa file).\n\nr0: Monster ID\nreturn: bool",
    )

    GetMonsterIdToSpawn = Symbol(
        [0xBB28],
        [0x22E9408],
        None,
        "Get the id of the monster to be randomly spawned.\n\nr0: the spawn weight to"
        " use (0 for normal, 1 for monster house)\nreturn: monster ID",
    )

    GetMonsterLevelToSpawn = Symbol(
        [0xBBE0],
        [0x22E94C0],
        None,
        "Get the level of the monster to be spawned, given its id.\n\nr0: monster"
        " ID\nreturn: Level of the monster to be spawned, or 1 if the specified ID"
        " can't be found on the floor's spawn table.",
    )

    GetDirectionTowardsPosition = Symbol(
        None,
        None,
        None,
        "Gets the direction in which a monster should move to go from the origin"
        " position to the target position\n\nr0: Origin position\nr1: Target"
        " position\nreturn: Direction in which to move to reach the target position"
        " from the origin position",
    )

    GetChebyshevDistance = Symbol(
        None,
        None,
        None,
        "Returns the Chebyshev distance between two positions. Calculated as"
        " max(abs(x0-x1), abs(y0-y1)).\n\nr0: Position A\nr1: Position B\nreturn:"
        " Chebyshev Distance between position A and position B",
    )

    IsPositionInSight = Symbol(
        None,
        None,
        None,
        "Checks if a given target position is in sight from a given origin"
        " position.\nThere's multiple factors that affect this check, but generally,"
        " it's true if both positions are in the same room or within 2 tiles of each"
        " other.\n\nr0: Origin position\nr1: Target position\nr2: True to assume the"
        " entity standing on the origin position has the dropeye status\nreturn: True"
        " if the target position is in sight from the origin position",
    )

    GetLeader = Symbol(
        None,
        None,
        None,
        "Gets the pointer to the entity that is currently leading the team, or null if"
        " none of the first 4 entities is a valid monster with its is_team_leader flag"
        " set. It also sets LEADER_PTR to the result before returning it.\n\nreturn:"
        " Pointer to the current leader of the team or null if there's no valid"
        " leader.",
    )

    TickStatusTurnCounter = Symbol(
        [0xD7CC],
        [0x22EB0AC],
        None,
        "Ticks down a turn counter for a status condition. If the counter equals 0x7F,"
        " it will not be decreased.\n\nr0: pointer to the status turn counter\nreturn:"
        " new counter value",
    )

    AdvanceFrame = Symbol(
        None,
        None,
        None,
        "Advances one frame. Does not return until the next frame starts.\n\nr0: ? -"
        " Unused by the function",
    )

    GenerateDungeonRngSeed = Symbol(
        [0xE708],
        [0x22EBFE8],
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
        [0xE754],
        [0x22EC034],
        None,
        "Gets the current preseed stored in the global dungeon PRNG state. See"
        " GenerateDungeonRngSeed for more information.\n\nreturn: current dungeon RNG"
        " preseed",
    )

    SetDungeonRngPreseed = Symbol(
        [0xE764],
        [0x22EC044],
        None,
        "Sets the preseed in the global dungeon PRNG state. See GenerateDungeonRngSeed"
        " for more information.\n\nr0: preseed",
    )

    InitDungeonRng = Symbol(
        [0xE774],
        [0x22EC054],
        None,
        "Initialize (or reinitialize) the dungeon PRNG with a given seed. The primary"
        " LCG and the five secondary LCGs are initialized jointly, and with the same"
        " seed.\n\nr0: seed",
    )

    DungeonRand16Bit = Symbol(
        [0xE7A8],
        [0x22EC088],
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
        [0xE820],
        [0x22EC100],
        None,
        "Compute a pseudorandom integer under a given maximum value using the dungeon"
        " PRNG.\n\nr0: high\nreturn: pseudorandom integer on the interval [0, high"
        " - 1]",
    )

    DungeonRandRange = Symbol(
        [0xE848],
        [0x22EC128],
        None,
        "Compute a pseudorandom value between two integers using the dungeon"
        " PRNG.\n\nr0: x\nr1: y\nreturn: pseudorandom integer on the interval [min(x,"
        " y), max(x, y) - 1]",
    )

    DungeonRandOutcome = Symbol(
        None,
        None,
        None,
        "Returns the result of a possibly biased coin flip (a Bernoulli random"
        " variable) with some success probability p, using the dungeon PRNG.\n\nr0:"
        " success percentage (100*p)\nreturn: true with probability p, false with"
        " probability (1-p)",
    )

    CalcStatusDuration = Symbol(
        [0xE908],
        [0x22EC1E8],
        None,
        "Seems to calculate the duration of a volatile status on a monster.\n\nr0:"
        " entity pointer\nr1: pointer to a turn range (an array of two shorts {lower,"
        " higher})\nr2: flag for whether or not to factor in the Self Curer IQ skill"
        " and the Natural Cure ability\nreturn: number of turns for the status"
        " condition",
    )

    DungeonRngUnsetSecondary = Symbol(
        [0xE9BC],
        [0x22EC29C],
        None,
        "Sets the dungeon PRNG to use the primary LCG for subsequent random number"
        " generation, and also resets the secondary LCG index back to 0.\n\nSimilar to"
        " DungeonRngSetPrimary, but DungeonRngSetPrimary doesn't modify the secondary"
        " LCG index if it was already set to something other than 0.\n\nNo params.",
    )

    DungeonRngSetSecondary = Symbol(
        [0xE9D4],
        [0x22EC2B4],
        None,
        "Sets the dungeon PRNG to use one of the 5 secondary LCGs for subsequent random"
        " number generation.\n\nr0: secondary LCG index",
    )

    DungeonRngSetPrimary = Symbol(
        None,
        None,
        None,
        "Sets the dungeon PRNG to use the primary LCG for subsequent random number"
        " generation.\n\nNo params.",
    )

    TrySwitchPlace = Symbol(
        [0xEF00],
        [0x22EC7E0],
        None,
        "The user entity attempts to switch places with the target entity (i.e. by the"
        " effect of the Switcher Orb). \n\nThe function checks for the Suction Cups"
        " ability for both the user and the target, and for the Mold Breaker ability on"
        " the user.\n\nr0: pointer to user entity\nr1: pointer to target entity",
    )

    ClearMonsterActionFields = Symbol(
        None,
        None,
        None,
        "Clears the fields related to AI in the monster's data struct, setting them all"
        " to 0.\nSpecifically, monster::action_id, monster::action_use_idx and"
        " monster::field_0x54 are cleared.\n\nr0: Pointer to the monster's action_id"
        " field (this field is probably contained in a struct)",
    )

    SetMonsterActionFields = Symbol(
        None,
        None,
        None,
        "Sets some the fields related to AI in the monster's data"
        " struct.\nSpecifically, monster::action_id, monster::action_use_idx and"
        " monster::field_0x54. The last 2 are always set to 0.\n\nr0: Pointer to the"
        " monster's action_id field (this field is probably contained in a struct)\nr1:"
        " Value to set monster::action_id to.",
    )

    SetActionPassTurnOrWalk = Symbol(
        None,
        None,
        None,
        "Sets a monster's action to action::ACTION_PASS_TURN or action::ACTION_WALK,"
        " depending on the result of GetCanMoveFlag for the monster's ID.\n\nr0:"
        " Pointer to the monster's action_id field (this field is probably contained in"
        " a struct)\nr1: Monster ID",
    )

    SetActionRegularAttack = Symbol(
        None,
        None,
        None,
        "Sets a monster's action to action::ACTION_REGULAR_ATTACK, with a specified"
        " direction.\n\nr0: Pointer to the monster's action_id field (this field is"
        " probably contained in a struct)\nr1: Direction in which to use the move. Gets"
        " stored in monster::direction.",
    )

    SetActionUseMoveAi = Symbol(
        None,
        None,
        None,
        "Sets a monster's action to action::ACTION_USE_MOVE_AI, with a specified"
        " direction and move index.\n\nr0: Pointer to the monster's action_id field"
        " (this field is probably contained in a struct)\nr1: Index of the move to use"
        " (0-3). Gets stored in monster::action_use_idx.\nr2: Direction in which to use"
        " the move. Gets stored in monster::direction.",
    )

    RunFractionalTurn = Symbol(
        [0xFA90],
        [0x22ED370],
        None,
        "The main function which executes the actions that take place in a fractional"
        " turn. Called in a loop by RunDungeon while IsFloorOver returns false.\n\nr0:"
        " first loop flag (true when the function is first called during a floor)",
    )

    RunLeaderTurn = Symbol(
        None,
        None,
        None,
        "Handles the leader's turn. Includes a movement speed check that might cause it"
        " to return early if the leader isn't fast enough to act in this fractional"
        " turn. If that check (and some others) pass, the function does not return"
        " until the leader performs an action.\n\nr0: ?\nreturn: true if the leader has"
        " performed an action",
    )

    TrySpawnMonsterAndActivatePlusMinus = Symbol(
        [0x10464],
        [0x22EDD44],
        None,
        "Called at the beginning of RunFractionalTurn. Executed only if"
        " FRACTIONAL_TURN_SEQUENCE[fractional_turn * 2] is not 0.\n\nFirst it calls"
        " TrySpawnMonsterAndTickSpawnCounter, then tries to activate the Plus and Minus"
        " abilities for both allies and enemies, and finally calls TryForcedLoss.\n\nNo"
        " params.",
    )

    IsFloorOver = Symbol(
        [0x10570],
        [0x22EDE50],
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
        None,
        None,
        None,
        "Decrements dungeon::wind_turns and displays a wind warning message if"
        " required.\n\nNo params.",
    )

    SetForcedLossReason = Symbol(
        None,
        None,
        None,
        "Sets dungeon::forced_loss_reason to the specified value\n\nr0: Forced loss"
        " reason",
    )

    GetForcedLossReason = Symbol(
        None,
        None,
        None,
        "Returns dungeon::forced_loss_reason\n\nreturn: forced_loss_reason",
    )

    ResetDamageDesc = Symbol(
        [0x1AB1C],
        [0x22F83FC],
        None,
        "Seems to zero some damage description struct, which is output by the damage"
        " calculation function.\n\nr0: damage description pointer",
    )

    GetSpriteIndex = Symbol(
        None,
        None,
        None,
        "Gets the sprite index of the specified monster on this floor\n\nr0: Monster"
        " ID\nreturn: Sprite index of the specified monster ID",
    )

    JoinedAtRangeCheck2Veneer = Symbol(
        None,
        None,
        None,
        "Likely a linker-generated veneer for arm9::JoinedAtRangeCheck2.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nNo"
        " params.",
    )

    FloorNumberIsEven = Symbol(
        [0x1B09C],
        [0x22F897C],
        None,
        "Checks if the current dungeon floor number is even.\n\nHas a special check to"
        " return false for Labyrinth Cave B10F (the Gabite boss fight).\n\nreturn:"
        " bool",
    )

    GetKecleonIdToSpawnByFloor = Symbol(
        [0x1B0D4],
        [0x22F89B4],
        None,
        "If the current floor number is even, returns female Kecleon's id (0x3D7),"
        " otherwise returns male Kecleon's id (0x17F).\n\nreturn: monster ID",
    )

    LoadMonsterSprite = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Handles a fainted pokémon (reviving does not count as fainting).\n\nr0:"
        " Fainted entity\nr1: Faint reason (move ID or greater than the max move id for"
        " other causes)\nr2: Entity responsible of the fainting",
    )

    UpdateAiTargetPos = Symbol(
        None,
        None,
        None,
        "Given a monster, updates its target_pos field based on its current position"
        " and the direction in which it plans to attack.\n\nr0: Entity pointer",
    )

    TryActivateSlowStart = Symbol(
        [0x1CF20],
        [0x22FA800],
        None,
        "Runs a check over all monsters on the field for the ability Slow Start, and"
        " lowers the speed of those who have it.\n\nNo params",
    )

    TryActivateArtificialWeatherAbilities = Symbol(
        [0x1CFBC],
        [0x22FA89C],
        None,
        "Runs a check over all monsters on the field for abilities that affect the"
        " weather and changes the floor's weather accordingly.\n\nNo params",
    )

    DefenderAbilityIsActive = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Checks if an entity is a monster (entity type 1).\n\nr0: entity"
        " pointer\nreturn: bool",
    )

    TryActivateTruant = Symbol(
        [0x1D4C8],
        [0x22FADA8],
        None,
        "Checks if an entity has the ability Truant, and if so tries to apply the pause"
        " status to it.\n\nr0: pointer to entity",
    )

    RestorePpAllMovesSetFlags = Symbol(
        None,
        None,
        None,
        "Restores PP for all moves, clears flags move::f_consume_2_pp,"
        " move::flags2_unk5 and move::flags2_unk7, and sets flag"
        " move::f_consume_pp.\nCalled when a monster is revived.\n\nr0: pointer to"
        " entity whose moves will be restored",
    )

    ShouldMonsterHeadToStairs = Symbol(
        None,
        None,
        None,
        "Checks if a given monster should try to reach the stairs when controlled by"
        " the AI\n\nr0: Entity pointer\nreturn: True if the monster should try to reach"
        " the stairs, false otherwise",
    )

    MewSpawnCheck = Symbol(
        [0x1E2B8],
        [0x22FBB98],
        None,
        "If the monster id parameter is 0x97 (Mew), returns false if either"
        " dungeon::mew_cannot_spawn or the second parameter are true.\n\nCalled before"
        " spawning an enemy, appears to be checking if Mew can spawn on the current"
        " floor.\n\nr0: monster id\nr1: return false if the monster id is Mew\nreturn:"
        " bool",
    )

    ExclusiveItemEffectIsActive = Symbol(
        None,
        None,
        None,
        "Checks if a monster is a team member under the effects of a certain exclusive"
        " item effect.\n\nr0: entity pointer\nr1: exclusive item effect ID\nreturn:"
        " bool",
    )

    GetTeamMemberWithIqSkill = Symbol(
        [0x1ECA0],
        [0x22FC580],
        None,
        "Returns an entity pointer to the first team member which has the specified iq"
        " skill.\n\nr0: iq skill id\nreturn: pointer to entity",
    )

    TeamMemberHasEnabledIqSkill = Symbol(
        [0x1ED0C],
        [0x22FC5EC],
        None,
        "Returns true if any team member has the specified iq skill.\n\nr0: iq skill"
        " id\nreturn: bool",
    )

    TeamLeaderIqSkillIsEnabled = Symbol(
        [0x1ED28],
        [0x22FC608],
        None,
        "Returns true the leader has the specified iq skill.\n\nr0: iq skill"
        " id\nreturn: bool",
    )

    HasLowHealth = Symbol(
        [0x1F204],
        [0x22FCAE4],
        None,
        "Checks if the entity passed is a valid monster, and if it's at low health"
        " (below 25% rounded down)\n\nr0: entity pointer\nreturn: bool",
    )

    IsSpecialStoryAlly = Symbol(
        [0x1F6C4],
        [0x22FCFA4],
        None,
        "Checks if a monster is a special story ally.\n\nThis is a hard-coded check"
        " that looks at the monster's 'Joined At' field. If the value is in the range"
        " [DUNGEON_JOINED_AT_BIDOOF, DUNGEON_DUMMY_0xE3], this check will return"
        " true.\n\nr0: monster pointer\nreturn: bool",
    )

    IsExperienceLocked = Symbol(
        [0x1F6E4],
        [0x22FCFC4],
        None,
        "Checks if a monster does not gain experience.\n\nThis basically just inverts"
        " IsSpecialStoryAlly, with the exception of also checking for the 'Joined At'"
        " field being DUNGEON_CLIENT (is this set for mission clients?).\n\nr0: monster"
        " pointer\nreturn: bool",
    )

    InitTeam = Symbol(
        None,
        None,
        None,
        "Seems to initialize the team when entering a dungeon.\n\nr0: ?",
    )

    SpawnMonster = Symbol(
        [0x20B98],
        [0x22FE478],
        None,
        "Spawns the given monster on a tile.\n\nr0: pointer to struct"
        " spawned_monster_data\nr1: if true, the monster cannot spawn asleep, otherwise"
        " it will randomly be asleep\nreturn: pointer to entity",
    )

    InitTeamMember = Symbol(
        None,
        None,
        None,
        "Initializes a team member. Run at the start of each floor in a dungeon.\n\nr0:"
        " Monster ID\nr1: First type\nr2: Second type\nr3: Pointer to the struct"
        " containing the data of the team member to initialize\nstack[0]: ?\nstack[1]:"
        " ?\nstack[2]: ?\nstack[3]: ?\nstack[4]: ?",
    )

    ExecuteMonsterAction = Symbol(
        None,
        None,
        None,
        "Executes the set action for the specified monster. Used for both AI actions"
        " and player-inputted actions. If the action is not ACTION_NOTHING,"
        " ACTION_PASS_TURN, ACTION_WALK or ACTION_UNK_4, the monster's already_acted"
        " field is set to true. Includes a switch based on the action ID that performs"
        " the action, although some of them aren't handled by said swtich.\n\nr0:"
        " Pointer to monster entity",
    )

    HasStatusThatPreventsActing = Symbol(
        None,
        None,
        None,
        "Returns true if the monster has any status problem that prevents it from"
        " acting\n\nr0: Entity pointer\nreturn: True if the specified monster can't act"
        " because of a status problem, false otherwise.",
    )

    CalcSpeedStage = Symbol(
        [0x23944],
        [0x2301224],
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
        None,
        None,
        None,
        "Calls CalcSpeedStage with a speed counter weight of 1.\n\nr0: pointer to"
        " entity\nreturn: speed stage",
    )

    GetNumberOfAttacks = Symbol(
        [0x23AAC],
        [0x230138C],
        None,
        "Returns the number of attacks that a monster can do in one turn (1 or"
        " 2).\n\nChecks for the abilities Swift Swim, Chlorophyll, Unburden, and for"
        " exclusive items.\n\nr0: pointer to entity\nreturns: int",
    )

    SprintfStatic = Symbol(
        [0x23DF0],
        [0x23016D0],
        None,
        "Statically defined copy of sprintf(3) in overlay 29. See arm9.yml for more"
        " information.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )

    IsMonsterCornered = Symbol(
        None,
        None,
        None,
        "True if the given monster is cornered (it can't move in any direction)\n\nr0:"
        " Entity pointer\nreturn: True if the monster can't move in any direction,"
        " false otherwise.",
    )

    CanAttackInDirection = Symbol(
        None,
        None,
        None,
        "Returns whether a monster can attack in a given direction.\nThe check fails if"
        " the destination tile is impassable, contains a monster that isn't of type"
        " entity_type::ENTITY_MONSTER or if the monster can't directly move from the"
        " current tile into the destination tile.\n\nr0: Entity pointer\nr1:"
        " Direction\nreturn: True if the monster can attack into the tile adjacent to"
        " them in the specified direction, false otherwise.",
    )

    CanAiMonsterMoveInDirection = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Checks if a monster should run away from other monsters\n\nr0: Entity"
        " pointer\nreturn: True if the monster should run away, false otherwise",
    )

    ShouldMonsterRunAwayVariation = Symbol(
        None,
        None,
        None,
        "Calls ShouldMonsterRunAway and returns its result. It also calls another"
        " function if the result was true.\n\nr0: Entity pointer\nr1: ?\nreturn: Result"
        " of the call to ShouldMonsterRunAway",
    )

    NoGastroAcidStatus = Symbol(
        [0x25954],
        [0x2303234],
        None,
        "Checks if a monster does not have the Gastro Acid status.\n\nr0: entity"
        " pointer\nreturn: bool",
    )

    AbilityIsActive = Symbol(
        [0x25988],
        [0x2303268],
        None,
        "Checks if a monster has a certain ability that isn't disabled by Gastro"
        " Acid.\n\nr0: entity pointer\nr1: ability ID\nreturn: bool",
    )

    LevitateIsActive = Symbol(
        [0x25A88],
        [0x2303368],
        None,
        "Checks if a monster is levitating (has the effect of Levitate and Gravity is"
        " not active).\n\nr0: pointer to entity\nreturn: bool",
    )

    MonsterIsType = Symbol(
        [0x25AC0],
        [0x23033A0],
        None,
        "Checks if a monster is a given type.\n\nr0: entity pointer\nr1: type"
        " ID\nreturn: bool",
    )

    CanSeeInvisibleMonsters = Symbol(
        None,
        None,
        None,
        "Returns whether a certain monster can see other invisible monsters.\nTo be"
        " precise, this function returns true if the monster is holding Goggle Specs or"
        " if it has the status status::STATUS_EYEDROPS.\n\nr0: Entity pointer\nreturn:"
        " True if the monster can see invisible monsters.",
    )

    HasDropeyeStatus = Symbol(
        None,
        None,
        None,
        "Returns whether a certain monster is under the effect of"
        " status::STATUS_DROPEYE.\n\nr0: Entity pointer\nreturn: True if the monster"
        " has dropeye status.",
    )

    IqSkillIsEnabled = Symbol(
        [0x25BF0],
        [0x23034D0],
        None,
        "Checks if a monster has a certain IQ skill enabled.\n\nr0: entity pointer\nr1:"
        " IQ skill ID\nreturn: bool",
    )

    GetMoveTypeForMonster = Symbol(
        None,
        None,
        None,
        "Check the type of a move when used by a certain monster. Accounts for special"
        " cases such as Hidden Power, Weather Ball, the regular attack...\n\nr0: Entity"
        " pointer\nr1: Pointer to move data\nreturn: Type of the move",
    )

    GetMovePower = Symbol(
        [0x25F8C],
        [0x230386C],
        None,
        "Gets the power of a move, factoring in Ginseng/Space Globe boosts.\n\nr0: user"
        " pointer\nr1: move pointer\nreturn: move power",
    )

    AddExpSpecial = Symbol(
        [0x261AC],
        [0x2303A8C],
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
        None,
        None,
        None,
        "Checks if the specified enemy should evolve because it just defeated an ally,"
        " and if so, attempts to evolve it.\n\nr0: Pointer to the enemy to check",
    )

    EvolveMonster = Symbol(
        None,
        None,
        None,
        "Makes the specified monster evolve into the specified species.\n\nr0: Pointer"
        " to the entity to evolve\nr1: ?\nr2: Species to evolve into",
    )

    GetSleepAnimationId = Symbol(
        [0x28724],
        [0x2306004],
        None,
        "Returns the animation id to be applied to a monster that has the sleep,"
        " napping, nightmare or bide status.\n\nReturns a different animation for"
        " sudowoodo and for monsters with infinite sleep turns (0x7F).\n\nr0: pointer"
        " to entity\nreturn: animation ID",
    )

    DisplayActions = Symbol(
        None,
        None,
        None,
        "Graphically displays any pending actions that have happened but haven't been"
        " shown on screen yet. All actions are displayed at the same time. For example,"
        " this delayed display system is used to display multiple monsters moving at"
        " once even though they take turns sequentially.\n\nr0: Pointer to an entity."
        " Can be null.\nreturns: Seems to be true if there were any pending actions to"
        " display.",
    )

    EndFrozenClassStatus = Symbol(
        [0x29EC8],
        [0x23077A8],
        None,
        "Cures the target's freeze, shadow hold, ingrain, petrified, constriction or"
        " wrap (both as user and as target) status due to the action of the"
        " user.\n\nr0: pointer to user\nr1: pointer to target\nr2: if true, the event"
        " will be printed to the log",
    )

    EndCringeClassStatus = Symbol(
        [0x2A024],
        [0x2307904],
        None,
        "Cures the target's cringe, confusion, cowering, pause, taunt, encore or"
        " infatuated status due to the action of the user, and prints the event to the"
        " log.\n\nr0: pointer to user\nr1: pointer to target",
    )

    RunMonsterAi = Symbol(
        None,
        None,
        None,
        "Runs the AI for a single monster to determine whether the monster can act and"
        " which action it should perform if so\n\nr0: Pointer to monster\nr1: ?",
    )

    ApplyDamage = Symbol(
        None,
        None,
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
        [0x2E8F0],
        [0x230C1D0],
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
        None,
        None,
        None,
        "Probably the damage calculation function.\n\nr0: attacker pointer\nr1:"
        " defender pointer\nr2: attack type\nr3: attack power\nstack[0]: crit"
        " chance\nstack[1]: [output] struct containing info about the damage"
        " calculation\nstack[2]: damage multiplier (as a binary fixed-point number with"
        " 8 fraction bits)\nstack[3]: move ID\nstack[4]: ?",
    )

    CalcRecoilDamageFixed = Symbol(
        [0x30DEC],
        [0x230E6CC],
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
        [0x30EA0],
        [0x230E780],
        None,
        "Appears to calculate damage from a fixed-damage effect.\n\nr0: attacker"
        " pointer\nr1: defender pointer\nr2: fixed damage\nr3: ?\nstack[0]: [output]"
        " struct containing info about the damage calculation\nstack[1]: attack"
        " type\nstack[2]: move category\nstack[3]: ?\nstack[4]: message"
        " type\nothers: ?",
    )

    CalcDamageFixedNoCategory = Symbol(
        [0x31004],
        [0x230E8E4],
        None,
        "A wrapper around CalcDamageFixed with the move category set to none.\n\nr0:"
        " attacker pointer\nr1: defender pointer\nr2: fixed damage\nstack[0]: [output]"
        " struct containing info about the damage calculation\nstack[1]: attack"
        " type\nothers: ?",
    )

    CalcDamageFixedWrapper = Symbol(
        [0x31050],
        [0x230E930],
        None,
        "A wrapper around CalcDamageFixed.\n\nr0: attacker pointer\nr1: defender"
        " pointer\nr2: fixed damage\nstack[0]: [output] struct containing info about"
        " the damage calculation\nstack[1]: attack type\nstack[2]: move"
        " category\nothers: ?",
    )

    ResetDamageCalcScratchSpace = Symbol(
        [0x31184],
        [0x230EA64],
        None,
        "CalcDamage seems to use scratch space of some kind, which this function"
        " zeroes.\n\nNo params.",
    )

    TrySpawnMonsterAndTickSpawnCounter = Symbol(
        [0x32318],
        [0x230FBF8],
        None,
        "First ticks up the spawn counter, and if it's equal or greater than the spawn"
        " cooldown, it will try to spawn an enemy if the number of enemies is below the"
        " spawn cap.\n\nIf the spawn counter is greater than 900, it will instead"
        " perform the special spawn caused by the ability Illuminate.\n\nNo params.",
    )

    AuraBowIsActive = Symbol(
        [0x33324],
        [0x2310C04],
        None,
        "Checks if a monster is holding an aura bow that isn't disabled by"
        " Klutz.\n\nr0: entity pointer\nreturn: bool",
    )

    ExclusiveItemOffenseBoost = Symbol(
        None,
        None,
        None,
        "Gets the exclusive item boost for attack/special attack for a monster\n\nr0:"
        " entity pointer\nr1: move category index (0 for physical, 1 for"
        " special)\nreturn: boost",
    )

    ExclusiveItemDefenseBoost = Symbol(
        None,
        None,
        None,
        "Gets the exclusive item boost for defense/special defense for a monster\n\nr0:"
        " entity pointer\nr1: move category index (0 for physical, 1 for"
        " special)\nreturn: boost",
    )

    TickNoSlipCap = Symbol(
        [0x337EC],
        [0x23110CC],
        None,
        "Checks if the entity is a team member and holds the No-Slip Cap, and if so"
        " attempts to make one item in the bag sticky.\n\nr0: pointer to entity",
    )

    TickStatusAndHealthRegen = Symbol(
        [0x34CD0],
        [0x23125B0],
        None,
        "Applies the natural HP regen effect by taking modifiers into account (Poison"
        " Heal, Heal Ribbon, weather-related regen). Then it ticks down counters for"
        " volatile status effects, and heals them if the counter reached zero.\n\nr0:"
        " pointer to entity",
    )

    InflictSleepStatusSingle = Symbol(
        [0x3545C],
        [0x2312D3C],
        None,
        "This is called by TryInflictSleepStatus.\n\nr0: entity pointer\nr1: number of"
        " turns",
    )

    TryInflictSleepStatus = Symbol(
        [0x35510],
        [0x2312DF0],
        None,
        "Inflicts the Sleep status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: number of turns\nr3: flag"
        " to log a message on failure",
    )

    TryInflictNightmareStatus = Symbol(
        [0x35878],
        [0x2313158],
        None,
        "Inflicts the Nightmare status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: number"
        " of turns",
    )

    TryInflictNappingStatus = Symbol(
        [0x35988],
        [0x2313268],
        None,
        "Inflicts the Napping status condition (from Rest) on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: number"
        " of turns",
    )

    TryInflictYawningStatus = Symbol(
        [0x35A94],
        [0x2313374],
        None,
        "Inflicts the Yawning status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: number of turns",
    )

    TryInflictSleeplessStatus = Symbol(
        [0x35BA4],
        [0x2313484],
        None,
        "Inflicts the Sleepless status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    TryInflictPausedStatus = Symbol(
        [0x35C90],
        [0x2313570],
        None,
        "Inflicts the Paused status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: ?\nr3: number of"
        " turns\nstack[0]: flag to log a message on failure\nstack[1]: flag to only"
        " perform the check for inflicting without actually inflicting\nreturn: Whether"
        " or not the status could be inflicted",
    )

    TryInflictInfatuatedStatus = Symbol(
        [0x35DD0],
        [0x23136B0],
        None,
        "Inflicts the Infatuated status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    TryInflictBurnStatus = Symbol(
        [0x35F58],
        [0x2313838],
        None,
        "Inflicts the Burn status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to apply some"
        " special effect alongside the burn?\nr3: flag to log a message on"
        " failure\nstack[0]: flag to only perform the check for inflicting without"
        " actually inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictBurnStatusWholeTeam = Symbol(
        [0x36234],
        [0x2313B14],
        None,
        "Inflicts the Burn status condition on all team members if possible.\n\nNo"
        " params.",
    )

    TryInflictPoisonedStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Poisoned status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictBadlyPoisonedStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Badly Poisoned status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    TryInflictFrozenStatus = Symbol(
        [0x3680C],
        [0x23140EC],
        None,
        "Inflicts the Frozen status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure",
    )

    TryInflictConstrictionStatus = Symbol(
        [0x36A30],
        [0x2314310],
        None,
        "Inflicts the Constriction status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2:"
        " animation ID\nr3: flag to log a message on failure",
    )

    TryInflictShadowHoldStatus = Symbol(
        [0x36B88],
        [0x2314468],
        None,
        "Inflicts the Shadow Hold (AKA Immobilized) status condition on a target"
        " monster if possible.\n\nr0: user entity pointer\nr1: target entity"
        " pointer\nr2: flag to log a message on failure",
    )

    TryInflictIngrainStatus = Symbol(
        [0x36D3C],
        [0x231461C],
        None,
        "Inflicts the Ingrain status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer",
    )

    TryInflictWrappedStatus = Symbol(
        [0x36E00],
        [0x23146E0],
        None,
        "Inflicts the Wrapped status condition on a target monster if possible.\n\nThis"
        " also gives the user the Wrap status (Wrapped around foe).\n\nr0: user entity"
        " pointer\nr1: target entity pointer",
    )

    FreeOtherWrappedMonsters = Symbol(
        [0x36FFC],
        [0x23148DC],
        None,
        "Frees from the wrap status all monsters which are wrapped by/around the"
        " monster passed as parameter.\n\nr0: pointer to entity",
    )

    TryInflictPetrifiedStatus = Symbol(
        [0x37078],
        [0x2314958],
        None,
        "Inflicts the Petrified status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    LowerOffensiveStat = Symbol(
        None,
        None,
        None,
        "Lowers the specified offensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of"
        " stages\nstack[0]: ?\nstack[1]: ?",
    )

    LowerDefensiveStat = Symbol(
        [0x3741C],
        [0x2314CFC],
        None,
        "Lowers the specified defensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of"
        " stages\nstack[0]: ?\nstack[1]: ?",
    )

    BoostOffensiveStat = Symbol(
        [0x375A4],
        [0x2314E84],
        None,
        "Boosts the specified offensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of stages",
    )

    BoostDefensiveStat = Symbol(
        [0x37710],
        [0x2314FF0],
        None,
        "Boosts the specified defensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of stages",
    )

    ApplyOffensiveStatMultiplier = Symbol(
        None,
        None,
        None,
        "Applies a multiplier to the specified offensive stat on the target"
        " monster.\n\nThis affects struct"
        " monster_stat_modifiers::offensive_multipliers, for moves like Charm and"
        " Memento.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: stat"
        " index\nr3: multiplier\nstack[0]: ?",
    )

    ApplyDefensiveStatMultiplier = Symbol(
        [0x37B64],
        [0x2315444],
        None,
        "Applies a multiplier to the specified defensive stat on the target"
        " monster.\n\nThis affects struct"
        " monster_stat_modifiers::defensive_multipliers, for moves like Screech.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: stat index\nr3:"
        " multiplier\nstack[0]: ?",
    )

    BoostHitChanceStat = Symbol(
        [0x37CE4],
        [0x23155C4],
        None,
        "Boosts the specified hit chance stat (accuracy or evasion) on the target"
        " monster.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: stat"
        " index",
    )

    LowerHitChanceStat = Symbol(
        [0x37E2C],
        [0x231570C],
        None,
        "Lowers the specified hit chance stat (accuracy or evasion) on the target"
        " monster.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: stat"
        " index\nr3: ?",
    )

    TryInflictCringeStatus = Symbol(
        [0x37FE4],
        [0x23158C4],
        None,
        "Inflicts the Cringe status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictParalysisStatus = Symbol(
        [0x3813C],
        [0x2315A1C],
        None,
        "Inflicts the Paralysis status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    BoostSpeed = Symbol(
        [0x38404],
        [0x2315CE4],
        None,
        "Boosts the speed of the target monster.\n\nIf the number of turns specified is"
        " 0, a random turn count will be selected using the default"
        " SPEED_BOOST_DURATION_RANGE.\n\nr0: user entity pointer\nr1: target entity"
        " pointer\nr2: number of stages\nr3: number of turns\nstack[0]: flag to log a"
        " message on failure",
    )

    BoostSpeedOneStage = Symbol(
        [0x38530],
        [0x2315E10],
        None,
        "A wrapper around BoostSpeed with the number of stages set to 1.\n\nr0: user"
        " entity pointer\nr1: target entity pointer\nr2: number of turns\nr3: flag to"
        " log a message on failure",
    )

    LowerSpeed = Symbol(
        [0x38548],
        [0x2315E28],
        None,
        "Lowers the speed of the target monster.\n\nr0: user entity pointer\nr1: target"
        " entity pointer\nr2: number of stages\nr3: flag to log a message on failure",
    )

    TrySealMove = Symbol(
        [0x386B0],
        [0x2315F90],
        None,
        "Seals one of the target monster's moves. The move to be sealed is randomly"
        " selected.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nreturn: Whether or not a move was sealed",
    )

    BoostOrLowerSpeed = Symbol(
        [0x38820],
        [0x2316100],
        None,
        "Randomly boosts or lowers the speed of the target monster by one stage with"
        " equal probability.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    ResetHitChanceStat = Symbol(
        [0x38880],
        [0x2316160],
        None,
        "Resets the specified hit chance stat (accuracy or evasion) back to normal on"
        " the target monster.\n\nr0: user entity pointer\nr1: target entity"
        " pointer\nr2: stat index\nr3: ?",
    )

    TryActivateQuickFeet = Symbol(
        [0x38A10],
        [0x23162F0],
        None,
        "Activate the Quick Feet ability on the defender, if the monster has it and"
        " it's active.\n\nr0: attacker pointer\nr1: defender pointer\nreturn: bool,"
        " whether or not the ability was activated",
    )

    TryInflictConfusedStatus = Symbol(
        [0x38B30],
        [0x2316410],
        None,
        "Inflicts the Confused status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictCoweringStatus = Symbol(
        [0x38E64],
        [0x2316744],
        None,
        "Inflicts the Cowering status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryIncreaseHp = Symbol(
        [0x38EDC],
        [0x23167BC],
        None,
        "Restore HP and possibly boost max HP of the target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: HP to restore\nr3: max HP"
        " boost\nstack[0]: flag to log a message on failure\nreturn: Success flag",
    )

    TryInflictLeechSeedStatus = Symbol(
        [0x393E4],
        [0x2316CC4],
        None,
        "Inflicts the Leech Seed status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    TryInflictDestinyBond = Symbol(
        [0x39648],
        [0x2316F28],
        None,
        "Inflicts the Destiny Bond status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    IsBlinded = Symbol(
        [0x3B3D4],
        [0x2318CB4],
        None,
        "Returns true if the monster has the blinded status (see statuses::blinded), or"
        " if it is not the leader and is holding Y-Ray Specs.\n\nr0: pointer to"
        " entity\nr1: flag for whether to check for the held item\nreturn: bool",
    )

    RestoreMovePP = Symbol(
        [0x3B810],
        [0x23190F0],
        None,
        "Restores the PP of all the target's moves by the specified amount.\n\nr0: user"
        " entity pointer\nr1: target entity pointer\nr2: PP to restore\nr3: flag to"
        " suppress message logging",
    )

    SetReflectDamageCountdownTo4 = Symbol(
        [0x3BFB0],
        [0x2319890],
        None,
        "Sets the monster's reflect damage countdown to a global value (0x4).\n\nr0:"
        " pointer to entity",
    )

    HasConditionalGroundImmunity = Symbol(
        [0x3C63C],
        [0x2319F1C],
        None,
        "Checks if a monster is currently immune to Ground-type moves for reasons other"
        " than typing and ability.\n\nThis includes checks for Gravity and Magnet"
        " Rise.\n\nr0: entity pointer\nreturn: bool",
    )

    Conversion2IsActive = Symbol(
        [0x3D404],
        [0x231ACE4],
        None,
        "Checks if the monster is under the effect of Conversion 2 (its type was"
        " changed).\n\nReturns 1 if the effects is a status, 2 if it comes from an"
        " exclusive item, 0 otherwise.\n\nr0: pointer to entity\nreturn: int",
    )

    AiConsiderMove = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        [0x3E284],
        [0x231BB64],
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
        [0x3E89C],
        [0x231C17C],
        None,
        "Gets the move target-and-range field when used by a given entity. See struct"
        " move_target_and_range in the C headers.\n\nr0: entity pointer\nr1: move"
        " pointer\nr2: AI flag (same as GetMoveTargetAndRange)\nreturn: move target and"
        " range",
    )

    ApplyItemEffect = Symbol(
        [0x3F278],
        [0x231CB58],
        None,
        "Seems to apply an item's effect via a giant switch statement?\n\nr3: attacker"
        " pointer\nstack[0]: defender pointer\nstack[1]: thrown item"
        " pointer\nothers: ?",
    )

    ViolentSeedBoost = Symbol(
        None,
        None,
        None,
        "Applies the Violent Seed boost to an entity.\n\nr0: attacker pointer\nr1:"
        " defender pointer",
    )

    ApplyGummiBoostsDungeonMode = Symbol(
        [0x40CA8],
        [0x231E588],
        None,
        "Applies the IQ and possible stat boosts from eating a Gummi to the target"
        " monster.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: Gummi"
        " type ID\nr3: Stat boost amount, if a random stat boost occurs",
    )

    GetMaxPpWrapper = Symbol(
        [0x425BC],
        [0x231FE9C],
        None,
        "Gets the maximum PP for a given move. A wrapper around the function in the ARM"
        " 9 binary.\n\nr0: move pointer\nreturn: max PP for the given move, capped"
        " at 99",
    )

    MoveIsNotPhysical = Symbol(
        [0x425E4],
        [0x231FEC4],
        None,
        "Checks if a move isn't a physical move.\n\nr0: move ID\nreturn: bool",
    )

    TryPounce = Symbol(
        [0x437EC],
        [0x23210CC],
        None,
        "Makes the target monster execute the Pounce action in a given direction if"
        " possible.\n\nIf the direction ID is 8, the target will pounce in the"
        " direction it's currently facing.\n\nr0: user entity pointer\nr1: target"
        " entity pointer\nr2: direction ID",
    )

    TryBlowAway = Symbol(
        [0x439AC],
        [0x232128C],
        None,
        "Blows away the target monster in a given direction if possible.\n\nr0: user"
        " entity pointer\nr1: target entity pointer\nr2: direction ID",
    )

    TryWarp = Symbol(
        [0x448D4],
        [0x23221B4],
        None,
        "Makes the target monster warp if possible.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: warp type\nr3: position (if warp type is"
        " position-based)",
    )

    MoveHitCheck = Symbol(
        None,
        None,
        None,
        "Determines if a move used hits or misses the target. It gets called twice per"
        " target, once with r3 = false and a second time with r3 = true.\n\nr0:"
        " Attacker\nr1: Defender\nr2: Pointer to move data\nr3: True if the move's"
        " first accuracy (accuracy1) should be used, false if its second accuracy"
        " (accuracy2) should be used instead.\nreturns: True if the move hits, false if"
        " it misses.",
    )

    DungeonRandOutcomeUserTargetInteraction = Symbol(
        [0x484E4],
        [0x2325DC4],
        None,
        "Like DungeonRandOutcome, but specifically for user-target"
        " interactions.\n\nThis modifies the underlying random process depending on"
        " factors like Serene Grace, and whether or not either entity has"
        " fainted.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: base"
        " success percentage (100*p). 0 is treated specially and guarantees success.",
    )

    DungeonRandOutcomeUserAction = Symbol(
        [0x485CC],
        [0x2325EAC],
        None,
        "Like DungeonRandOutcome, but specifically for user actions.\n\nThis modifies"
        " the underlying random process to factor in Serene Grace (and checks whether"
        " the user is a valid entity).\n\nr0: entity pointer\nr1: base success"
        " percentage (100*p). 0 is treated specially and guarantees success.",
    )

    CanAiUseMove = Symbol(
        None,
        None,
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
        None,
        None,
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
        [0x48938],
        [0x2326218],
        None,
        "Updates the PP of any moves that were used by a monster, if PP should be"
        " consumed.\n\nr0: entity pointer\nr1: flag for whether or not PP should be"
        " consumed",
    )

    LowerSshort = Symbol(
        [0x48A10],
        [0x23262F0],
        None,
        "Gets the lower 2 bytes of a 4-byte number and interprets it as a signed"
        " short.\n\nr0: 4-byte number x\nreturn: (short) x",
    )

    GetMoveAnimationId = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Checks whether a moved used by a monster should play its alternative"
        " animation. Includes checks for Curse, Snore, Sleep Talk, Solar Beam and"
        " 2-turn moves.\n\nr0: Pointer to the entity that used the move\nr1: Move"
        " pointer\nreturn: True if the move should play its alternative animation",
    )

    DealDamageWithRecoil = Symbol(
        [0x4BADC],
        [0x23293BC],
        None,
        "Deals damage from a move or item used by an attacking monster on a defending"
        " monster, and also deals recoil damage to the attacker.\n\nr0: attacker"
        " pointer\nr1: defender pointer\nr2: move\nr3: item ID\nreturn: bool, whether"
        " or not damage was dealt",
    )

    ExecuteMoveEffect = Symbol(
        None,
        None,
        None,
        "Handles the effects that happen after a move is used. Includes a loop that is"
        " run for each target, mutiple ability checks and the giant switch statement"
        " that executes the effect of the move used given its ID.\n\nr0: pointer to"
        " some struct\nr1: attacker pointer\nr2: pointer to move data\nr3:"
        " ?\nstack[0]: ?",
    )

    DealDamage = Symbol(
        [0x56630],
        [0x2333F10],
        None,
        "Deals damage from a move or item used by an attacking monster on a defending"
        " monster.\n\nr0: attacker pointer\nr1: defender pointer\nr2: move\nr3: damage"
        " multiplier (as a binary fixed-point number with 8 fraction bits)\nstack[0]:"
        " item ID\nreturn: amount of damage dealt",
    )

    CalcDamageProjectile = Symbol(
        [0x5675C],
        [0x233403C],
        None,
        "Appears to calculate damage from a variable-damage projectile.\n\nr0: entity"
        " pointer 1?\nr1: entity pointer 2?\nr2: move pointer\nr3: move"
        " power\nothers: ?",
    )

    CalcDamageFinal = Symbol(
        None,
        None,
        None,
        "Last function called by DealDamage to determine the final damage dealt by the"
        " move. The result of this call is the return value of DealDamage. \n\nr0:"
        " Attacker pointer\nr1: Defender pointer\nr2: Move pointer\nr3: ?\nstack[0]:"
        " Pointer to some struct. The first byte contains the ID of the move used.",
    )

    StatusCheckerCheck = Symbol(
        None,
        None,
        None,
        "Determines if using a given move against its intended targets would be"
        " redundant because all of them already have the effect caused by said"
        " move.\n\nr0: Pointer to the entity that is considering using the move\nr1:"
        " Move pointer\nreturn: True if it makes sense to use the move, false if it"
        " would be redundant given the effects it causes and the effects that all the"
        " targets already have.",
    )

    GetApparentWeather = Symbol(
        [0x58814],
        [0x23360F4],
        None,
        "Get the weather, as experienced by a specific entity.\n\nr0: entity"
        " pointer\nreturn: weather ID",
    )

    TryWeatherFormChange = Symbol(
        [0x58C7C],
        [0x233655C],
        None,
        "Tries to change a monster into one of its weather-related alternative forms."
        " Applies to Castform and Cherrim, and checks for their unique"
        " abilities.\n\nr0: pointer to entity",
    )

    GetTile = Symbol(
        [0x59BEC],
        [0x23374CC],
        None,
        "Get the tile at some position. If the coordinates are out of bounds, returns a"
        " default tile.\n\nr0: x position\nr1: y position\nreturn: tile pointer",
    )

    GetTileSafe = Symbol(
        [0x59C54],
        [0x2337534],
        None,
        "Get the tile at some position. If the coordinates are out of bounds, returns a"
        " pointer to a copy of the default tile.\n\nr0: x position\nr1: y"
        " position\nreturn: tile pointer",
    )

    GetStairsRoom = Symbol(
        None,
        None,
        None,
        "Returns the index of the room that contains the stairs\n\nreturn: Room index",
    )

    GravityIsActive = Symbol(
        None, None, None, "Checks if gravity is active on the floor.\n\nreturn: bool"
    )

    IsSecretBazaar = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is the Secret Bazaar.\n\nreturn: bool",
    )

    IsSecretRoom = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is the Secret Room fixed floor (from hidden"
        " stairs).\n\nreturn: bool",
    )

    IsSecretFloor = Symbol(
        [0x5C168],
        [0x2339A48],
        None,
        "Checks if the current floor is a secret bazaar or a secret room.\n\nreturn:"
        " bool",
    )

    GetDungeonGenInfoUnk0C = Symbol(
        None, None, None, "return: dungeon_generation_info::field_0xc"
    )

    GetMinimapData = Symbol(
        None,
        None,
        None,
        "Returns a pointer to the minimap_display_data struct in the dungeon"
        " struct.\n\nreturn: minimap_display_data*",
    )

    SetMinimapDataE447 = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Sets minimap_display_data::field_0xE448 to the specified value\n\nr0: Value to"
        " set the field to",
    )

    LoadFixedRoomDataVeneer = Symbol(
        None,
        None,
        None,
        "Likely a linker-generated veneer for LoadFixedRoomData.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nNo"
        " params.",
    )

    IsNormalFloor = Symbol(
        [0x5E138],
        [0x233BA18],
        None,
        "Checks if the current floor is a normal layout.\n\n'Normal' means any layout"
        " that is NOT one of the following:\n- Hidden stairs floors\n- Golden"
        " Chamber\n- Challenge Request floor\n- Outlaw hideout\n- Treasure Memo"
        " floor\n- Full-room fixed floors (ID < 0xA5) [0xA5 == Sealed"
        " Chamber]\n\nreturn: bool",
    )

    GenerateFloor = Symbol(
        [0x5E1BC],
        [0x233BA9C],
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
        [0x5E95C],
        [0x233C23C],
        None,
        "Gets the terrain type of a tile.\n\nr0: tile pointer\nreturn: terrain ID",
    )

    DungeonRand100 = Symbol(
        [0x5E968],
        [0x233C248],
        None,
        "Compute a pseudorandom integer on the interval [0, 100) using the dungeon"
        " PRNG.\n\nreturn: pseudorandom integer",
    )

    FlagHallwayJunctions = Symbol(
        [0x5E9F0],
        [0x233C2D0],
        None,
        "Sets the junction flag (bit 3 of the terrain flags) on any hallway junction"
        " tiles in some range [x0, x1), [y0, y1). This leaves tiles within rooms"
        " untouched.\n\nA hallway tile is considered a junction if it has at least 3"
        " cardinal neighbors with open terrain.\n\nr0: x0\nr1: y0\nr2: x1\nr3: y1",
    )

    GenerateStandardFloor = Symbol(
        [0x5EB0C],
        [0x233C3EC],
        None,
        "Generate a standard floor with the given parameters.\n\nBroadly speaking, a"
        " standard floor is generated as follows:\n1. Generating the grid\n2. Creating"
        " a room or hallway anchor in each grid cell\n3. Creating hallways between grid"
        " cells\n4. Generating special features (maze room, Kecleon shop, Monster"
        " House, extra hallways, room imperfections, secondary structures)\n\nr0: grid"
        " size x\nr1: grid size y\nr2: floor properties",
    )

    GenerateOuterRingFloor = Symbol(
        [0x5EC74],
        [0x233C554],
        None,
        "Generates a floor layout with a 4x2 grid of rooms, surrounded by an outer ring"
        " of hallways.\n\nr0: floor properties",
    )

    GenerateCrossroadsFloor = Symbol(
        [0x5F100],
        [0x233C9E0],
        None,
        "Generates a floor layout with a mesh of hallways on the interior 3x2 grid,"
        " surrounded by a boundary of rooms protruding from the interior like spikes,"
        " excluding the corner cells.\n\nr0: floor properties",
    )

    GenerateLineFloor = Symbol(
        [0x5F560],
        [0x233CE40],
        None,
        "Generates a floor layout with 5 grid cells in a horizontal line.\n\nr0: floor"
        " properties",
    )

    GenerateCrossFloor = Symbol(
        [0x5F6C0],
        [0x233CFA0],
        None,
        "Generates a floor layout with 5 rooms arranged in a cross ('plus sign')"
        " formation.\n\nr0: floor properties",
    )

    GenerateBeetleFloor = Symbol(
        [0x5F858],
        [0x233D138],
        None,
        "Generates a floor layout in a 'beetle' formation, which is created by taking a"
        " 3x3 grid of rooms, connecting the rooms within each row, and merging the"
        " central column into one big room.\n\nr0: floor properties",
    )

    MergeRoomsVertically = Symbol(
        [0x5FA14],
        [0x233D2F4],
        None,
        "Merges two vertically stacked rooms into one larger room.\n\nr0: x grid"
        " coordinate of the rooms to merge\nr1: y grid coordinate of the upper"
        " room\nr2: dy, where the lower room has a y grid coordinate of y+dy\nr3: grid"
        " to update",
    )

    GenerateOuterRoomsFloor = Symbol(
        [0x5FB60],
        [0x233D440],
        None,
        "Generates a floor layout with a ring of rooms on the grid boundary and nothing"
        " in the interior.\n\nNote that this function is bugged, and won't properly"
        " connect all the rooms together for grid_size_x < 4.\n\nr0: grid size x\nr1:"
        " grid size y\nr2: floor properties",
    )

    IsNotFullFloorFixedRoom = Symbol(
        [0x5FDF4],
        [0x233D6D4],
        None,
        "Checks if a fixed room ID does not correspond to a fixed, full-floor"
        " layout.\n\nThe first non-full-floor fixed room is 0xA5, which is for Sealed"
        " Chambers.\n\nr0: fixed room ID\nreturn: bool",
    )

    GenerateFixedRoom = Symbol(
        None,
        None,
        None,
        "Handles fixed room generation if the floor contains a fixed room.\n\nr0: fixed"
        " room ID\nr1: floor properties\nreturn: bool",
    )

    GenerateOneRoomMonsterHouseFloor = Symbol(
        [0x60254],
        [0x233DB34],
        None,
        "Generates a floor layout with just a large, one-room Monster House.\n\nThis is"
        " the default layout if dungeon generation fails.\n\nNo params.",
    )

    GenerateTwoRoomsWithMonsterHouseFloor = Symbol(
        [0x60324],
        [0x233DC04],
        None,
        "Generate a floor layout with two rooms (left and right), one of which is a"
        " Monster House.\n\nNo params.",
    )

    GenerateExtraHallways = Symbol(
        [0x604C8],
        [0x233DDA8],
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
        [0x60A64],
        [0x233E344],
        None,
        "Get the grid cell positions for a given set of floor grid dimensions.\n\nr0:"
        " [output] pointer to array of the starting x coordinates of each grid"
        " column\nr1: [output] pointer to array of the starting y coordinates of each"
        " grid row\nr2: grid size x\nr3: grid size y",
    )

    InitDungeonGrid = Symbol(
        [0x60AE4],
        [0x233E3C4],
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
        [0x60BE4],
        [0x233E4C4],
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
        [0x60DF8],
        [0x233E6D8],
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
        [0x61154],
        [0x233EA34],
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
        [0x61B3C],
        [0x233F41C],
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
        [0x61F1C],
        [0x233F7FC],
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
        [0x62814],
        [0x23400F4],
        None,
        "Attempt to generate room imperfections for each room in the floor layout, if"
        " enabled.\n\nEach room has a 40% chance of having imperfections if its grid"
        " cell is flagged to allow room imperfections. Imperfections are generated by"
        " randomly growing the walls of the room inwards for a certain number of"
        " iterations, starting from the corners.\n\nr0: grid to update\nr1: grid size"
        " x\nr2: grid size y",
    )

    CreateHallway = Symbol(
        [0x62C00],
        [0x23404E0],
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
        [0x62F04],
        [0x23407E4],
        None,
        "Ensure the grid forms a connected graph (all valid cells are reachable) by"
        " adding hallways to unreachable grid cells.\n\nIf a grid cell cannot be"
        " connected for some reason, remove it entirely.\n\nr0: grid to update\nr1:"
        " grid size x\nr2: grid size y\nr3: array of the starting x coordinates of each"
        " grid column\nstack[0]: array of the starting y coordinates of each grid row",
    )

    SetTerrainObstacleChecked = Symbol(
        [0x633E0],
        [0x2340CC0],
        None,
        "Set the terrain of a specific tile to be an obstacle (wall or secondary"
        " terrain).\n\nSecondary terrain (water/lava) can only be placed in the"
        " specified room. If the tile room index does not match, a wall will be placed"
        " instead.\n\nr0: tile pointer\nr1: use secondary terrain flag (true for"
        " water/lava, false for wall)\nr2: room index",
    )

    FinalizeJunctions = Symbol(
        [0x6341C],
        [0x2340CFC],
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
        [0x636C8],
        [0x2340FA8],
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
        [0x63A7C],
        [0x234135C],
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
        [0x63D04],
        [0x23415E4],
        None,
        "Possibly generate a maze room on the floor.\n\nA maze room will be generated"
        " with a probability determined by the maze room chance parameter. A maze will"
        " be generated in a random room that is valid, connected, has odd dimensions,"
        " and has no other features.\n\nr0: grid to update\nr1: grid size x\nr2: grid"
        " size y\nr3: maze room chance (percentage from 0-100)",
    )

    GenerateMaze = Symbol(
        [0x63F38],
        [0x2341818],
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
        [0x641B4],
        [0x2341A94],
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
        [0x6435C],
        [0x2341C3C],
        None,
        "Set spawn flag 5 (0b100000 or 0x20) on all tiles in a room.\n\nr0: grid cell",
    )

    IsNextToHallway = Symbol(
        [0x643B0],
        [0x2341C90],
        None,
        "Checks if a tile position is either in a hallway or next to one.\n\nr0: x\nr1:"
        " y\nreturn: bool",
    )

    ResolveInvalidSpawns = Symbol(
        [0x64454],
        [0x2341D34],
        None,
        "Resolve invalid spawn flags on tiles.\n\nSpawn flags can be invalid due to"
        " terrain. For example, traps can't spawn on obstacles. Spawn flags can also be"
        " invalid due to multiple being set on a single tile, in which case one will"
        " take precedence. For example, stair spawns trump trap spawns.\n\nNo params.",
    )

    ConvertSecondaryTerrainToChasms = Symbol(
        [0x644EC],
        [0x2341DCC],
        None,
        "Converts all secondary terrain tiles (water/lava) to chasms.\n\nNo params.",
    )

    EnsureImpassableTilesAreWalls = Symbol(
        [0x64558],
        [0x2341E38],
        None,
        "Ensures all tiles with the impassable flag are walls.\n\nNo params.",
    )

    InitializeTile = Symbol(
        [0x645B4], [0x2341E94], None, "Initialize a tile struct.\n\nr0: tile pointer"
    )

    ResetFloor = Symbol(
        [0x645EC],
        [0x2341ECC],
        None,
        "Resets the floor in preparation for a floor generation attempt.\n\nResets all"
        " tiles, resets the border to be impassable, and clears entity spawns.\n\nNo"
        " params.",
    )

    PosIsOutOfBounds = Symbol(
        [0x6478C],
        [0x234206C],
        None,
        "Checks if a position (x, y) is out of bounds on the map: !((0 <= x <= 55) &&"
        " (0 <= y <= 31)).\n\nr0: x\nr1: y\nreturn: bool",
    )

    ShuffleSpawnPositions = Symbol(
        [0x647C4],
        [0x23420A4],
        None,
        "Randomly shuffle an array of spawn positions.\n\nr0: spawn position array"
        " containing bytes {x1, y1, x2, y2, ...}\nr1: number of (x, y) pairs in the"
        " spawn position array",
    )

    SpawnNonEnemies = Symbol(
        [0x6482C],
        [0x234210C],
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
        [0x64F50],
        [0x2342830],
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
        [0x6524C],
        [0x2342B2C],
        None,
        "Set a specific tile to have secondary terrain (water/lava), but only if it's a"
        " passable wall.\n\nr0: tile pointer",
    )

    GenerateSecondaryTerrainFormations = Symbol(
        [0x6528C],
        [0x2342B6C],
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
        [0x6594C],
        [0x234322C],
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
        [0x66028], [0x2343908], None, "Converts all wall tiles to chasms.\n\nNo params."
    )

    ResetInnerBoundaryTileRows = Symbol(
        [0x6665C],
        [0x2343F3C],
        None,
        "Reset the inner boundary tile rows (y == 1 and y == 30) to their initial state"
        " of all wall tiles, with impassable walls at the edges (x == 0 and x =="
        " 55).\n\nNo params.",
    )

    SpawnStairs = Symbol(
        [0x6676C],
        [0x234404C],
        None,
        "Spawn stairs at the given location.\n\nIf the hidden stairs flag is set,"
        " hidden stairs will be spawned instead of normal stairs.\n\nIf spawning normal"
        " stairs and the current floor is a rescue floor, the room containing the"
        " stairs will be converted into a Monster House.\n\nr0: position (two-byte"
        " array for {x, y})\nr1: dungeon generation info pointer (a field on the"
        " dungeon struct)\nr2: hidden stairs flag",
    )

    LoadFixedRoomData = Symbol(
        [0x67874],
        [0x2345154],
        None,
        "Loads fixed room data from BALANCE/fixed.bin into the buffer pointed to by"
        " FIXED_ROOM_DATA_PTR.\n\nNo params.",
    )

    IsHiddenStairsFloor = Symbol(
        [0x67FF0],
        [0x23458D0],
        None,
        "Checks if the current floor is either the Secret Bazaar or a Secret"
        " Room.\n\nreturn: bool",
    )

    HasHeldItem = Symbol(
        [0x6A2B4],
        [0x2347B94],
        None,
        "Checks if a monster has a certain held item.\n\nr0: entity pointer\nr1: item"
        " ID\nreturn: bool",
    )

    IsOutlawOrChallengeRequestFloor = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is an active mission destination of type"
        " MISSION_TAKE_ITEM_FROM_OUTLAW, MISSION_ARREST_OUTLAW or"
        " MISSION_CHALLENGE_REQUEST.\n\nreturn: bool",
    )

    IsCurrentMissionType = Symbol(
        [0x6CC64],
        [0x234A544],
        None,
        "Checks if the current floor is an active mission destination of a given type"
        " (and any subtype).\n\nr0: mission type\nreturn: bool",
    )

    IsCurrentMissionTypeExact = Symbol(
        [0x6CC98],
        [0x234A578],
        None,
        "Checks if the current floor is an active mission destination of a given type"
        " and subtype.\n\nr0: mission type\nr1: mission subtype\nreturn: bool",
    )

    IsOutlawMonsterHouseFloor = Symbol(
        [0x6CCD4],
        [0x234A5B4],
        None,
        "Checks if the current floor is a mission destination for a Monster House"
        " outlaw mission.\n\nreturn: bool",
    )

    IsGoldenChamber = Symbol(
        [0x6CCF8],
        [0x234A5D8],
        None,
        "Checks if the current floor is a Golden Chamber floor.\n\nreturn: bool",
    )

    IsLegendaryChallengeFloor = Symbol(
        [0x6CD1C],
        [0x234A5FC],
        None,
        "Checks if the current floor is a boss floor for a Legendary Challenge Letter"
        " mission.\n\nreturn: bool",
    )

    IsJirachiChallengeFloor = Symbol(
        [0x6CD5C],
        [0x234A63C],
        None,
        "Checks if the current floor is the boss floor in Star Cave Pit for Jirachi's"
        " Challenge Letter mission.\n\nreturn: bool",
    )

    IsDestinationFloorWithMonster = Symbol(
        [0x6CD94],
        [0x234A674],
        None,
        "Checks if the current floor is a mission destination floor with a special"
        " monster.\n\nSee FloorHasMissionMonster for details.\n\nreturn: bool",
    )

    LoadMissionMonsterSprites = Symbol(
        None,
        None,
        None,
        "Loads the sprites of monsters that appear on the current floor because of a"
        " mission, if applicable.\n\nThis includes monsters to be rescued, outlaws and"
        " its minions.\n\nNo params.",
    )

    MissionTargetEnemyIsDefeated = Symbol(
        [0x6CEB8],
        [0x234A798],
        None,
        "Checks if the target enemy of the mission on the current floor has been"
        " defeated.\n\nreturn: bool",
    )

    SetMissionTargetEnemyDefeated = Symbol(
        [0x6CED8],
        [0x234A7B8],
        None,
        "Set the flag for whether or not the target enemy of the current mission has"
        " been defeated.\n\nr0: new flag value",
    )

    IsDestinationFloorWithFixedRoom = Symbol(
        [0x6CEEC],
        [0x234A7CC],
        None,
        "Checks if the current floor is a mission destination floor with a fixed"
        " room.\n\nThe entire floor can be a fixed room layout, or it can just contain"
        " a Sealed Chamber.\n\nreturn: bool",
    )

    GetItemToRetrieve = Symbol(
        [0x6CF14],
        [0x234A7F4],
        None,
        "Get the ID of the item that needs to be retrieve on the current floor for a"
        " mission, if one exists.\n\nreturn: item ID",
    )

    GetItemToDeliver = Symbol(
        [0x6CF38],
        [0x234A818],
        None,
        "Get the ID of the item that needs to be delivered to a mission client on the"
        " current floor, if one exists.\n\nreturn: item ID",
    )

    GetSpecialTargetItem = Symbol(
        [0x6CF64],
        [0x234A844],
        None,
        "Get the ID of the special target item for a Sealed Chamber or Treasure Memo"
        " mission on the current floor.\n\nreturn: item ID",
    )

    IsDestinationFloorWithItem = Symbol(
        [0x6CFAC],
        [0x234A88C],
        None,
        "Checks if the current floor is a mission destination floor with a special"
        " item.\n\nThis excludes missions involving taking an item from an"
        " outlaw.\n\nreturn: bool",
    )

    IsDestinationFloorWithHiddenOutlaw = Symbol(
        [0x6D00C],
        [0x234A8EC],
        None,
        "Checks if the current floor is a mission destination floor with a 'hidden"
        " outlaw' that behaves like a normal enemy.\n\nreturn: bool",
    )

    IsDestinationFloorWithFleeingOutlaw = Symbol(
        [0x6D030],
        [0x234A910],
        None,
        "Checks if the current floor is a mission destination floor with a 'fleeing"
        " outlaw' that runs away.\n\nreturn: bool",
    )

    GetMissionTargetEnemy = Symbol(
        [0x6D068],
        [0x234A948],
        None,
        "Get the monster ID of the target enemy to be defeated on the current floor for"
        " a mission, if one exists.\n\nreturn: monster ID",
    )

    GetMissionEnemyMinionGroup = Symbol(
        [0x6D080],
        [0x234A960],
        None,
        "Get the monster ID of the specified minion group on the current floor for a"
        " mission, if it exists.\n\nNote that a single minion group can correspond to"
        " multiple actual minions of the same species. There can be up to 2 minion"
        " groups.\n\nr0: minion group index (0-indexed)\nreturn: monster ID",
    )

    SetTargetMonsterNotFoundFlag = Symbol(
        None,
        None,
        None,
        "Sets dungeon::target_monster_not_found_flag to the specified value.\n\nr0:"
        " Value to set the flag to",
    )

    GetTargetMonsterNotFoundFlag = Symbol(
        None,
        None,
        None,
        "Gets the value of dungeon::target_monster_not_found_flag.\n\nreturn:"
        " dungeon::target_monster_not_found_flag",
    )

    FloorHasMissionMonster = Symbol(
        [0x6D190],
        [0x234AA70],
        None,
        "Checks if a given floor is a mission destination with a special monster,"
        " either a target to rescue or an enemy to defeat.\n\nMission types with a"
        " monster on the destination floor:\n- Rescue client\n- Rescue target\n- Escort"
        " to target\n- Deliver item\n- Search for target\n- Take item from outlaw\n-"
        " Arrest outlaw\n- Challenge Request\n\nr0: mission destination info"
        " pointer\nreturn: bool",
    )

    LogMessageByIdWithPopupCheckUser = Symbol(
        [0x6EC34],
        [0x234C514],
        None,
        "Logs a message in the message log alongside a message popup, if the user"
        " hasn't fainted.\n\nr0: user entity pointer\nr1: message ID",
    )

    LogMessageWithPopupCheckUser = Symbol(
        [0x6EC74],
        [0x234C554],
        None,
        "Logs a message in the message log alongside a message popup, if the user"
        " hasn't fainted.\n\nr0: user entity pointer\nr1: message string",
    )

    LogMessageByIdQuiet = Symbol(
        [0x6ECAC],
        [0x234C58C],
        None,
        "Logs a message in the message log (but without a message popup).\n\nr0: user"
        " entity pointer\nr1: message ID",
    )

    LogMessageQuiet = Symbol(
        [0x6ECD0],
        [0x234C5B0],
        None,
        "Logs a message in the message log (but without a message popup).\n\nr0: user"
        " entity pointer\nr1: message string",
    )

    LogMessageByIdWithPopupCheckUserTarget = Symbol(
        [0x6ECE0],
        [0x234C5C0],
        None,
        "Logs a message in the message log alongside a message popup, if some user"
        " check passes and the target hasn't fainted.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: message ID",
    )

    LogMessageWithPopupCheckUserTarget = Symbol(
        [0x6ED34],
        [0x234C614],
        None,
        "Logs a message in the message log alongside a message popup, if some user"
        " check passes and the target hasn't fainted.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: message string",
    )

    LogMessageByIdQuietCheckUserTarget = Symbol(
        [0x6ED80],
        [0x234C660],
        None,
        "Logs a message in the message log (but without a message popup), if some user"
        " check passes and the target hasn't fainted.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: message ID",
    )

    LogMessageByIdWithPopupCheckUserUnknown = Symbol(
        [0x6EDD4],
        [0x234C6B4],
        None,
        "Logs a message in the message log alongside a message popup, if the user"
        " hasn't fainted and some other unknown check.\n\nr0: user entity pointer\nr1:"
        " ?\nr2: message ID",
    )

    LogMessageByIdWithPopup = Symbol(
        [0x6EE28],
        [0x234C708],
        None,
        "Logs a message in the message log alongside a message popup.\n\nr0: user"
        " entity pointer\nr1: message ID",
    )

    LogMessageWithPopup = Symbol(
        None,
        None,
        None,
        "Logs a message in the message log alongside a message popup.\n\nr0: user"
        " entity pointer\nr1: message string",
    )

    LogMessage = Symbol(
        [0x6EE98],
        [0x234C778],
        None,
        "Logs a message in the message log.\n\nr0: user entity pointer\nr1: message"
        " string\nr2: bool, whether or not to present a message popup",
    )

    LogMessageById = Symbol(
        [0x6F0A4],
        [0x234C984],
        None,
        "Logs a message in the message log.\n\nr0: user entity pointer\nr1: message"
        " ID\nr2: bool, whether or not to present a message popup",
    )

    OpenMessageLog = Symbol(
        None, None, None, "Opens the message log window.\n\nr0: ?\nr1: ?"
    )

    RunDungeonMode = Symbol(
        [0x6F8AC],
        [0x234D18C],
        None,
        "This appears to be the top-level function for running dungeon mode.\n\nIt gets"
        " called by some code in overlay 10 right after doing the dungeon fade"
        " transition, and once it exits, the dungeon results are processed.\n\nThis"
        " function is presumably in charge of allocating the dungeon struct, setting it"
        " up, launching the dungeon engine, etc.",
    )

    DisplayDungeonTip = Symbol(
        None,
        None,
        None,
        "Checks if a given dungeon tip should be displayed at the start of a floor and"
        " if so, displays it. Called up to 4 times at the start of each new floor, with"
        " a different r0 parameter each time.\n\nr0: Pointer to the message_tip struct"
        " of the message that should be displayed\nr1: True to log the message in the"
        " message log",
    )

    SetBothScreensWindowColorToDefault = Symbol(
        [0x708E4],
        [0x234E1C4],
        None,
        "This changes the palettes of windows in both screens to an appropiate value"
        " depending on the playthrough\nIf you're in a special episode, they turn green"
        " , otherwise, they turn blue or pink depending on your character's sex\n\nNo"
        " params",
    )

    DisplayMessage = Symbol(
        None,
        None,
        None,
        "Displays a message in a dialogue box that optionally waits for player input"
        " before closing.\n\nr0: ?\nr1: ID of the string to display\nr2: True to wait"
        " for player input before closing the dialogue box, false to close it"
        " automatically once all the characters get printed.",
    )

    DisplayMessage2 = Symbol(None, None, None, "Very similar to DisplayMessage")

    DisplayMessageInternal = Symbol(
        None,
        None,
        None,
        "Called by DisplayMessage. Seems to be the function that handles the display of"
        " the dialogue box. It won't return until all the characters have been written"
        " and after the player manually closes the dialogue box (if the corresponding"
        " parameter was set).\n\nr0: ID of the string to display\nr1: True to wait for"
        " player input before closing the dialogue box, false to close it automatically"
        " once all the characters get printed.\nr2: ? (r0 in DisplayMessage)\nr3:"
        " ?\nstack[0]: ?\nstack[1]: ?",
    )


class JpOverlay29Data:
    DUNGEON_STRUCT_SIZE = Symbol(
        None, None, None, "Size of the dungeon struct (0x2CB14)"
    )

    MAX_HP_CAP = Symbol(
        None, None, None, "The maximum amount of HP a monster can have (999)."
    )

    OFFSET_OF_DUNGEON_FLOOR_PROPERTIES = Symbol(
        None,
        None,
        None,
        "Offset of the floor properties field in the dungeon struct (0x286B2)",
    )

    SPAWN_RAND_MAX = Symbol(
        None,
        None,
        None,
        "Equal to 10,000 (0x2710). Used as parameter for DungeonRandInt to generate the"
        " random number which determines the entity to spawn.",
    )

    DUNGEON_PRNG_LCG_MULTIPLIER = Symbol(
        None,
        None,
        None,
        "The multiplier shared by all of the dungeon PRNG's LCGs, 1566083941"
        " (0x5D588B65).",
    )

    DUNGEON_PRNG_LCG_INCREMENT_SECONDARY = Symbol(
        None,
        None,
        None,
        "The increment for the dungeon PRNG's secondary LCGs, 2531011 (0x269EC3). This"
        " happens to be the same increment that the Microsoft Visual C++ runtime"
        " library uses in its implementation of the rand() function.",
    )

    KECLEON_FEMALE_ID = Symbol(
        None,
        None,
        None,
        "0x3D7 (983). Used when spawning Kecleon on an even numbered floor.",
    )

    KECLEON_MALE_ID = Symbol(
        None,
        None,
        None,
        "0x17F (383). Used when spawning Kecleon on an odd numbered floor.",
    )

    MSG_ID_SLOW_START = Symbol(
        None,
        None,
        None,
        "ID of the message printed when a monster has the ability Slow Start at the"
        " beginning of the floor.",
    )

    EXPERIENCE_POINT_GAIN_CAP = Symbol(
        None,
        None,
        None,
        "A cap on the experience that can be given to a monster in one call to"
        " AddExpSpecial",
    )

    JUDGMENT_MOVE_ID = Symbol(
        None, None, None, "Move ID for Judgment (0x1D3)\n\ntype: enum move_id"
    )

    REGULAR_ATTACK_MOVE_ID = Symbol(
        None, None, None, "Move ID for the regular attack (0x163)\n\ntype: enum move_id"
    )

    DEOXYS_ATTACK_ID = Symbol(
        None,
        None,
        None,
        "Monster ID for Deoxys in Attack Forme (0x1A3)\n\ntype: enum monster_id",
    )

    DEOXYS_SPEED_ID = Symbol(
        None,
        None,
        None,
        "Monster ID for Deoxys in Speed Forme (0x1A5)\n\ntype: enum monster_id",
    )

    GIRATINA_ALTERED_ID = Symbol(
        None,
        None,
        None,
        "Monster ID for Giratina in Altered Forme (0x211)\n\ntype: enum monster_id",
    )

    PUNISHMENT_MOVE_ID = Symbol(
        None, None, None, "Move ID for Punishment (0x1BD)\n\ntype: enum move_id"
    )

    OFFENSE_STAT_MAX = Symbol(
        None,
        None,
        None,
        "Cap on an attacker's modified offense (attack or special attack) stat after"
        " boosts. Used during damage calculation.",
    )

    PROJECTILE_MOVE_ID = Symbol(
        None,
        None,
        None,
        "The move ID of the special 'projectile' move (0x195)\n\ntype: enum move_id",
    )

    BELLY_LOST_PER_TURN = Symbol(
        None,
        None,
        None,
        "The base value by which belly is decreased every turn.\n\nIts raw value is"
        " 0x199A, which encodes a binary fixed-point number (16 fraction bits) with"
        " value (0x199A * 2^-16), and is the closest approximation to 0.1 representable"
        " in this number format.",
    )

    MOVE_TARGET_AND_RANGE_SPECIAL_USER_HEALING = Symbol(
        None,
        None,
        None,
        "The move target and range code for special healing moves that target just the"
        " user (0x273).\n\ntype: struct move_target_and_range (+ padding)",
    )

    PLAIN_SEED_VALUE = Symbol(
        None, None, None, "Some value related to the Plain Seed (0xBE9)."
    )

    MAX_ELIXIR_PP_RESTORATION = Symbol(
        None,
        None,
        None,
        "The amount of PP restored per move by ingesting a Max Elixir (0x3E7).",
    )

    SLIP_SEED_VALUE = Symbol(
        None, None, None, "Some value related to the Slip Seed (0xC75)."
    )

    CASTFORM_NORMAL_FORM_MALE_ID = Symbol(
        None, None, None, "Castform's male normal form ID (0x17B)"
    )

    CASTFORM_NORMAL_FORM_FEMALE_ID = Symbol(
        None, None, None, "Castform's female normal form ID (0x3D3)"
    )

    CHERRIM_SUNSHINE_FORM_MALE_ID = Symbol(
        None, None, None, "Cherrim's male sunshine form ID (0x1CD)"
    )

    CHERRIM_OVERCAST_FORM_FEMALE_ID = Symbol(
        None, None, None, "Cherrim's female overcast form ID (0x424)"
    )

    CHERRIM_SUNSHINE_FORM_FEMALE_ID = Symbol(
        None, None, None, "Cherrim's female sunshine form ID (0x425)"
    )

    FLOOR_GENERATION_STATUS_PTR = Symbol(
        None,
        None,
        None,
        "Pointer to the global FLOOR_GENERATION_STATUS\n\ntype: struct"
        " floor_generation_status*",
    )

    OFFSET_OF_DUNGEON_N_NORMAL_ITEM_SPAWNS = Symbol(
        None,
        None,
        None,
        "Offset of the (number of base items + 1) field on the dungeon struct"
        " (0x12AFA)",
    )

    DUNGEON_GRID_COLUMN_BYTES = Symbol(
        None,
        None,
        None,
        "The number of bytes in one column of the dungeon grid cell array, 450, which"
        " corresponds to a column of 15 grid cells.",
    )

    DEFAULT_MAX_POSITION = Symbol(
        None,
        None,
        None,
        "A large number (9999) to use as a default position for keeping track of"
        " min/max position values",
    )

    OFFSET_OF_DUNGEON_GUARANTEED_ITEM_ID = Symbol(
        None,
        None,
        None,
        "Offset of the guaranteed item ID field in the dungeon struct (0x2C9E8)",
    )

    FIXED_ROOM_TILE_SPAWN_TABLE = Symbol(
        None,
        None,
        None,
        "Table of tiles that can spawn in fixed rooms, pointed into by the"
        " FIXED_ROOM_TILE_SPAWN_TABLE.\n\nThis is an array of 11 4-byte entries"
        " containing info about one tile each. Info includes the trap ID if a trap,"
        " room ID, and flags.\n\ntype: struct fixed_room_tile_spawn_entry[11]",
    )

    FIXED_ROOM_REVISIT_OVERRIDES = Symbol(
        None,
        None,
        None,
        "Table of fixed room IDs, which if nonzero, overrides the normal fixed room ID"
        " for a floor (which is used to index the table) if the dungeon has already"
        " been cleared previously.\n\nOverrides are used to substitute different fixed"
        " room data for things like revisits to story dungeons.\n\ntype: struct"
        " fixed_room_id_8[256]",
    )

    FIXED_ROOM_MONSTER_SPAWN_TABLE = Symbol(
        None,
        None,
        None,
        "Table of monsters that can spawn in fixed rooms, pointed into by the"
        " FIXED_ROOM_ENTITY_SPAWN_TABLE.\n\nThis is an array of 120 4-byte entries"
        " containing info about one monster each. Info includes the monster ID, stats,"
        " and behavior type.\n\ntype: struct fixed_room_monster_spawn_entry[120]",
    )

    FIXED_ROOM_ITEM_SPAWN_TABLE = Symbol(
        None,
        None,
        None,
        "Table of items that can spawn in fixed rooms, pointed into by the"
        " FIXED_ROOM_ENTITY_SPAWN_TABLE.\n\nThis is an array of 63 8-byte entries"
        " containing one item ID each.\n\ntype: struct fixed_room_item_spawn_entry[63]",
    )

    FIXED_ROOM_ENTITY_SPAWN_TABLE = Symbol(
        None,
        None,
        None,
        "Table of entities (items, monsters, tiles) that can spawn in fixed rooms,"
        " which is indexed into by the main data structure for each fixed room.\n\nThis"
        " is an array of 269 entries. Each entry contains 3 pointers (one into"
        " FIXED_ROOM_ITEM_SPAWN_TABLE, one into FIXED_ROOM_MONSTER_SPAWN_TABLE, and one"
        " into FIXED_ROOM_TILE_SPAWN_TABLE), and represents the entities that can spawn"
        " on one specific tile in a fixed room.\n\ntype: struct"
        " fixed_room_entity_spawn_entry[269]",
    )

    STATUS_ICON_ARRAY_MUZZLED = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::muzzled * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_MAGNET_RISE = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::magnet_rise * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_MIRACLE_EYE = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::miracle_eye * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_LEECH_SEED = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::leech_seed * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_LONG_TOSS = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::long_toss * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_BLINDED = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::blinded * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_BURN = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::burn * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_SURE_SHOT = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::sure_shot * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_INVISIBLE = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::invisible * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_SLEEP = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::sleep * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_CURSE = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::curse * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_FREEZE = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::freeze * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_CRINGE = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::cringe * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_BIDE = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::bide * 8. See UpdateStatusIconFlags for details.",
    )

    STATUS_ICON_ARRAY_REFLECT = Symbol(
        None,
        None,
        None,
        "Array of bit masks used to set monster::status_icon. Indexed by"
        " monster::statuses::reflect * 8. See UpdateStatusIconFlags for details.",
    )

    DIRECTIONS_XY = Symbol(
        None,
        None,
        None,
        "An array mapping each direction index to its x and y"
        " displacements.\n\nDirections start with 0=down and proceed counterclockwise"
        " (see enum direction_id). Displacements for x and y are interleaved and"
        " encoded as 2-byte signed integers. For example, the first two integers are"
        " [0, 1], which correspond to the x and y displacements for the 'down'"
        " direction (positive y means down).",
    )

    FRACTIONAL_TURN_SEQUENCE = Symbol(
        None,
        None,
        None,
        "Read by certain functions that are called by RunFractionalTurn to see if they"
        " should be executed.\n\nArray is accessed via a pointer added to some multiple"
        " of fractional_turn, so that if the resulting memory location is zero, the"
        " function returns.",
    )

    BELLY_DRAIN_IN_WALLS_INT = Symbol(
        None,
        None,
        None,
        "The additional amount by which belly is decreased every turn when inside walls"
        " (integer part)",
    )

    BELLY_DRAIN_IN_WALLS_THOUSANDTHS = Symbol(
        None,
        None,
        None,
        "The additional amount by which belly is decreased every turn when inside walls"
        " (fractional thousandths)",
    )

    SPATK_STAT_IDX = Symbol(
        None,
        None,
        None,
        "The index (1) of the special attack entry in internal stat structs, such as"
        " the stat modifier array for a monster.",
    )

    ATK_STAT_IDX = Symbol(
        None,
        None,
        None,
        "The index (0) of the attack entry in internal stat structs, such as the stat"
        " modifier array for a monster.",
    )

    CORNER_CARDINAL_NEIGHBOR_IS_OPEN = Symbol(
        None,
        None,
        None,
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
        None,
        None,
        None,
        "[Runtime] Pointer to the dungeon struct in dungeon mode.\n\nThis is a 'working"
        " copy' of DUNGEON_PTR_MASTER. The main dungeon engine uses this pointer (or"
        " rather pointers to this pointer) when actually running dungeon mode.\n\ntype:"
        " struct dungeon*",
    )

    DUNGEON_PTR_MASTER = Symbol(
        None,
        None,
        None,
        "[Runtime] Pointer to the dungeon struct in dungeon mode.\n\nThis is a 'master"
        " copy' of the dungeon pointer. The game uses this pointer when doing low-level"
        " memory work (allocation, freeing, zeroing). The normal DUNGEON_PTR is used"
        " for most other dungeon mode work.\n\ntype: struct dungeon*",
    )

    LEADER_PTR = Symbol(
        None,
        None,
        None,
        "[Runtime] Pointer to the current leader of the team.\n\ntype: struct entity*",
    )

    DUNGEON_PRNG_STATE = Symbol(
        None,
        None,
        None,
        "[Runtime] The global PRNG state for dungeon mode, not including the current"
        " values in the secondary sequences.\n\nThis struct holds state for the primary"
        " LCG, as well as the current configuration controlling which LCG to use when"
        " generating random numbers. See DungeonRand16Bit for more information on how"
        " the dungeon PRNG works.\n\ntype: struct prng_state",
    )

    DUNGEON_PRNG_STATE_SECONDARY_VALUES = Symbol(
        None,
        None,
        None,
        "[Runtime] An array of 5 integers corresponding to the last value generated for"
        " each secondary LCG sequence.\n\nBased on the assembly, this appears to be its"
        " own global array, separate from DUNGEON_PRNG_STATE.",
    )

    EXCL_ITEM_EFFECTS_WEATHER_ATK_SPEED_BOOST = Symbol(
        None,
        None,
        None,
        "Array of IDs for exclusive item effects that increase attack speed with"
        " certain weather conditions.",
    )

    EXCL_ITEM_EFFECTS_WEATHER_MOVE_SPEED_BOOST = Symbol(
        None,
        None,
        None,
        "Array of IDs for exclusive item effects that increase movement speed with"
        " certain weather conditions.",
    )

    EXCL_ITEM_EFFECTS_WEATHER_NO_STATUS = Symbol(
        None,
        None,
        None,
        "Array of IDs for exclusive item effects that grant status immunity with"
        " certain weather conditions.",
    )

    EXCL_ITEM_EFFECTS_EVASION_BOOST = Symbol(
        None,
        None,
        None,
        "Array of IDs for exclusive item effects that grant an evasion boost with"
        " certain weather conditions.",
    )

    DEFAULT_TILE = Symbol(
        None,
        None,
        None,
        "The default tile struct.\n\nThis is just a struct full of zeroes, but is used"
        " as a fallback in various places where a 'default' tile is needed, such as"
        " when a grid index is out of range.\n\ntype: struct tile",
    )

    FIXED_ROOM_DATA_PTR = Symbol(
        None,
        None,
        None,
        "[Runtime] Pointer to decoded fixed room data loaded from the BALANCE/fixed.bin"
        " file.",
    )

    NECTAR_IQ_BOOST = Symbol(None, None, None, "IQ boost from ingesting Nectar.")


class JpOverlay29Section:
    name = "overlay29"
    description = (
        "The dungeon engine.\n\nThis is the 'main' overlay of dungeon mode. It controls"
        " most things that happen in a Mystery Dungeon, such as dungeon layout"
        " generation, dungeon menus, enemy AI, and generally just running each turn"
        " while within a dungeon."
    )
    loadaddress = 0x22DD8E0
    length = 0x77200
    functions = JpOverlay29Functions
    data = JpOverlay29Data


class JpOverlay11Functions:
    FuncThatCallsCommandParsing = Symbol([0xF24], [0x22DE804], None, "")

    ScriptCommandParsing = Symbol([0x1B24], [0x22DF404], None, "")

    SsbLoad2 = Symbol([0x8448], [0x22E5D28], None, "")

    StationLoadHanger = Symbol([0x8920], [0x22E6200], None, "")

    ScriptStationLoadTalk = Symbol([0x9130], [0x22E6A10], None, "")

    SsbLoad1 = Symbol([0x9A9C], [0x22E737C], None, "")

    ScriptSpecialProcessCall = Symbol(
        [0xAE6C],
        [0x22E874C],
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
        [0xBD90],
        [0x22E9670],
        None,
        "Returns an entry from RECRUITMENT_TABLE_SPECIES.\n\nNote: This indexes without"
        " doing bounds checking.\n\nr0: index into RECRUITMENT_TABLE_SPECIES\nreturn:"
        " enum monster_id",
    )

    PrepareMenuAcceptTeamMember = Symbol(
        [0xBDD4],
        [0x22E96B4],
        None,
        "Implements SPECIAL_PROC_PREPARE_MENU_ACCEPT_TEAM_MEMBER (see"
        " ScriptSpecialProcessCall).\n\nr0: index into RECRUITMENT_TABLE_SPECIES",
    )

    InitRandomNpcJobs = Symbol(
        [0xBE78],
        [0x22E9758],
        None,
        "Implements SPECIAL_PROC_INIT_RANDOM_NPC_JOBS (see"
        " ScriptSpecialProcessCall).\n\nr0: job type? 0 is a random NPC job, 1 is a"
        " bottle mission\nr1: ?",
    )

    GetRandomNpcJobType = Symbol(
        [0xBF10],
        [0x22E97F0],
        None,
        "Implements SPECIAL_PROC_GET_RANDOM_NPC_JOB_TYPE (see"
        " ScriptSpecialProcessCall).\n\nreturn: job type?",
    )

    GetRandomNpcJobSubtype = Symbol(
        [0xBF28],
        [0x22E9808],
        None,
        "Implements SPECIAL_PROC_GET_RANDOM_NPC_JOB_SUBTYPE (see"
        " ScriptSpecialProcessCall).\n\nreturn: job subtype?",
    )

    GetRandomNpcJobStillAvailable = Symbol(
        [0xBF44],
        [0x22E9824],
        None,
        "Implements SPECIAL_PROC_GET_RANDOM_NPC_JOB_STILL_AVAILABLE (see"
        " ScriptSpecialProcessCall).\n\nreturn: bool",
    )

    AcceptRandomNpcJob = Symbol(
        [0xBFAC],
        [0x22E988C],
        None,
        "Implements SPECIAL_PROC_ACCEPT_RANDOM_NPC_JOB (see"
        " ScriptSpecialProcessCall).\n\nreturn: bool",
    )

    GroundMainLoop = Symbol(
        [0xC4C8],
        [0x22E9DA8],
        None,
        "Appears to be the main loop for ground mode.\n\nBased on debug print"
        " statements and general code structure, it seems contain a core loop, and"
        " dispatches to various functions in response to different events.\n\nr0: mode,"
        " which is stored globally and used in switch statements for dispatch\nreturn:"
        " return code",
    )

    GetAllocArenaGround = Symbol(
        [0xD0B0],
        [0x22EA990],
        None,
        "The GetAllocArena function used for ground mode. See SetMemAllocatorParams for"
        " more information.\n\nr0: initial memory arena pointer, or null\nr1: flags"
        " (see MemAlloc)\nreturn: memory arena pointer, or null",
    )

    GetFreeArenaGround = Symbol(
        [0xD114],
        [0x22EA9F4],
        None,
        "The GetFreeArena function used for ground mode. See SetMemAllocatorParams for"
        " more information.\n\nr0: initial memory arena pointer, or null\nr1: pointer"
        " to free\nreturn: memory arena pointer, or null",
    )

    GroundMainReturnDungeon = Symbol(
        [0xD168],
        [0x22EAA48],
        None,
        "Implements SPECIAL_PROC_RETURN_DUNGEON (see ScriptSpecialProcessCall).\n\nNo"
        " params.",
    )

    GroundMainNextDay = Symbol(
        [0xD18C],
        [0x22EAA6C],
        None,
        "Implements SPECIAL_PROC_NEXT_DAY (see ScriptSpecialProcessCall).\n\nNo"
        " params.",
    )

    JumpToTitleScreen = Symbol(
        [0xD330],
        [0x22EAC10],
        None,
        "Implements SPECIAL_PROC_JUMP_TO_TITLE_SCREEN and SPECIAL_PROC_0x1A (see"
        " ScriptSpecialProcessCall).\n\nr0: int, argument value for"
        " SPECIAL_PROC_JUMP_TO_TITLE_SCREEN and -1 for SPECIAL_PROC_0x1A\nreturn: bool"
        " (but note that the special process ignores this and always returns 0)",
    )

    ReturnToTitleScreen = Symbol(
        [0xD3E8],
        [0x22EACC8],
        None,
        "Implements SPECIAL_PROC_RETURN_TO_TITLE_SCREEN (see"
        " ScriptSpecialProcessCall).\n\nr0: fade duration\nreturn: bool (but note that"
        " the special process ignores this and always returns 0)",
    )

    ScriptSpecialProcess0x16 = Symbol(
        [0xD448],
        [0x22EAD28],
        None,
        "Implements SPECIAL_PROC_0x16 (see ScriptSpecialProcessCall).\n\nr0: bool",
    )

    SprintfStatic = Symbol(
        [0x2CB98],
        [0x230A478],
        None,
        "Statically defined copy of sprintf(3) in overlay 11. See arm9.yml for more"
        " information.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )

    StatusUpdate = Symbol(
        [0x3771C],
        [0x2314FFC],
        None,
        "Implements SPECIAL_PROC_STATUS_UPDATE (see ScriptSpecialProcessCall).\n\nNo"
        " params.",
    )


class JpOverlay11Data:
    SCRIPT_OP_CODES = Symbol(
        [0x3C294],
        [0x2319B74],
        0xBF8,
        "Table of opcodes for the script engine. There are 383 8-byte entries.\n\nThese"
        " opcodes underpin the various ExplorerScript functions you can call in the"
        " SkyTemple SSB debugger.\n\ntype: struct script_opcode_table",
    )

    C_ROUTINES = Symbol(
        [0x404AC],
        [0x231DD8C],
        0x15E8,
        "Common routines used within the unionall.ssb script (the master script). There"
        " are 701 8-byte entries.\n\nThese routines underpin the ExplorerScript"
        " coroutines you can call in the SkyTemple SSB debugger.\n\ntype: struct"
        " common_routine_table",
    )

    OBJECTS = Symbol(
        [0x42AD8],
        [0x23203B8],
        0x1A04,
        "Table of objects for the script engine, which can be placed in scenes. There"
        " are a version-dependent number of 12-byte entries.\n\ntype: struct"
        " script_object[length / 12]",
    )

    RECRUITMENT_TABLE_LOCATIONS = Symbol(
        None,
        None,
        None,
        "Table of dungeon IDs corresponding to entries in"
        " RECRUITMENT_TABLE_SPECIES.\n\ntype: struct dungeon_id_16[22]",
    )

    RECRUITMENT_TABLE_LEVELS = Symbol(
        None,
        None,
        None,
        "Table of levels for recruited Pokémon, corresponding to entries in"
        " RECRUITMENT_TABLE_SPECIES.\n\ntype: uint16_t[22]",
    )

    RECRUITMENT_TABLE_SPECIES = Symbol(
        None,
        None,
        None,
        "Table of Pokémon recruited at special locations, such as at the ends of"
        " certain dungeons (e.g., Dialga or the Seven Treasures legendaries) or during"
        " a cutscene (e.g., Cresselia and Manaphy).\n\nInterestingly, this includes"
        " both Heatran genders. It also includes Darkrai for some reason?\n\ntype:"
        " struct monster_id_16[22]",
    )

    LEVEL_TILEMAP_LIST = Symbol(None, None, None, "")

    OVERLAY11_OVERLAY_LOAD_TABLE = Symbol(
        None,
        None,
        None,
        "The overlays that can be loaded while this one is loaded.\n\nEach entry is 16"
        " bytes, consisting of:\n- overlay group ID (see arm9.yml or enum"
        " overlay_group_id in the C headers for a mapping between group ID and overlay"
        " number)\n- function pointer to entry point\n- function pointer to"
        " destructor\n- possibly function pointer to frame-update function?",
    )

    UNIONALL_RAM_ADDRESS = Symbol(None, None, None, "[Runtime]")

    GROUND_STATE_MAP = Symbol(None, None, None, "[Runtime]")

    GROUND_STATE_PTRS = Symbol(
        None,
        None,
        None,
        "Host pointers to multiple structure used for performing an overworld"
        " scene\n\ntype: struct main_ground_data",
    )


class JpOverlay11Section:
    name = "overlay11"
    description = (
        "The script engine.\n\nThis is the 'main' overlay of ground mode. The script"
        " engine is what runs the ground mode scripts contained in the SCRIPT folder,"
        " which are written in a custom scripting language. These scripts encode things"
        " like cutscenes, screen transitions, ground mode events, and tons of other"
        " things related to ground mode."
    )
    loadaddress = 0x22DD8E0
    length = 0x48B00
    functions = JpOverlay11Functions
    data = JpOverlay11Data


class JpOverlay25Functions:
    pass


class JpOverlay25Data:
    APPRAISAL_MENU_CONFIRM = Symbol(None, None, None, "")

    APPRAISAL_MAIN_MENU = Symbol(None, None, None, "")

    APPRAISAL_SUBMENU = Symbol(None, None, None, "")


class JpOverlay25Section:
    name = "overlay25"
    description = "Controls Xatu Appraisal."
    loadaddress = 0x238B6A0
    length = 0x14C0
    functions = JpOverlay25Functions
    data = JpOverlay25Data


class JpArm9Functions:
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

    GetRngSeed = Symbol(None, None, None, "Get the current value of PRNG_SEQUENCE_NUM.")

    SetRngSeed = Symbol(
        None, None, None, "Seed PRNG_SEQUENCE_NUM to a given value.\n\nr0: seed"
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Functionally the same as Sprintf, just defined statically in many different"
        " places.\n\nSince this is essentially just a wrapper around vsprintf(3), this"
        " function was probably statically defined in a header somewhere and included"
        " in a bunch of different places. See the actual Sprintf for the one in"
        " libc.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of characters"
        " printed, excluding the null-terminator",
    )

    SetMoneyCarried = Symbol(
        [0xED4C],
        [0x200ED4C],
        None,
        "Sets the amount of money the player is carrying, clamping the value to the"
        " range [0, MAX_MONEY_CARRIED].\n\nr0: new value",
    )

    IsBagFull = Symbol(
        [0xEDF0],
        [0x200EDF0],
        None,
        "Implements SPECIAL_PROC_IS_BAG_FULL (see ScriptSpecialProcessCall).\n\nreturn:"
        " bool",
    )

    CountItemTypeInBag = Symbol(
        [0xEEB8],
        [0x200EEB8],
        None,
        "Implements SPECIAL_PROC_COUNT_ITEM_TYPE_IN_BAG (see"
        " ScriptSpecialProcessCall).\n\nr0: item ID\nreturn: number of items of the"
        " specified ID in the bag",
    )

    AddItemToBag = Symbol(
        [0xF81C],
        [0x200F81C],
        None,
        "Implements SPECIAL_PROC_ADD_ITEM_TO_BAG (see ScriptSpecialProcessCall).\n\nr0:"
        " pointer to an owned_item\nreturn: bool",
    )

    ScriptSpecialProcess0x39 = Symbol(
        [0xFD24],
        [0x200FD24],
        None,
        "Implements SPECIAL_PROC_0x39 (see ScriptSpecialProcessCall).\n\nreturn: bool",
    )

    CountItemTypeInStorage = Symbol(
        [0xFEB4],
        [0x200FEB4],
        None,
        "Implements SPECIAL_PROC_COUNT_ITEM_TYPE_IN_STORAGE (see"
        " ScriptSpecialProcessCall).\n\nr0: pointer to an owned_item\nreturn: number of"
        " items of the specified ID in storage",
    )

    RemoveItemsTypeInStorage = Symbol(
        [0x101B4],
        [0x20101B4],
        None,
        "Probably? Implements SPECIAL_PROC_0x2A (see ScriptSpecialProcessCall).\n\nr0:"
        " pointer to an owned_item\nreturn: bool",
    )

    AddItemToStorage = Symbol(
        [0x102EC],
        [0x20102EC],
        None,
        "Implements SPECIAL_PROC_ADD_ITEM_TO_STORAGE (see"
        " ScriptSpecialProcessCall).\n\nr0: pointer to an owned_item\nreturn: bool",
    )

    SetMoneyStored = Symbol(
        [0x106F4],
        [0x20106F4],
        None,
        "Sets the amount of money the player has stored in the Duskull Bank, clamping"
        " the value to the range [0, MAX_MONEY_STORED].\n\nr0: new value",
    )

    GetExclusiveItemOffset = Symbol(
        [0x10E10],
        [0x2010E10],
        None,
        "Gets the exclusive item offset, which is the item ID relative to that of the"
        " first exclusive item, the Prism Ruff.\n\nr0: item ID\nreturn: offset",
    )

    ApplyExclusiveItemStatBoosts = Symbol(
        [0x10E34],
        [0x2010E34],
        None,
        "Applies stat boosts from an exclusive item.\n\nr0: item ID\nr1: pointer to"
        " attack stat to modify\nr2: pointer to special attack stat to modify\nr3:"
        " pointer to defense stat to modify\nstack[0]: pointer to special defense stat"
        " to modify",
    )

    SetExclusiveItemEffect = Symbol(
        [0x10F50],
        [0x2010F50],
        None,
        "Sets the bit for an exclusive item effect.\n\nr0: pointer to the effects"
        " bitvector to modify\nr1: exclusive item effect ID",
    )

    ExclusiveItemEffectFlagTest = Symbol(
        [0x10F74],
        [0x2010F74],
        None,
        "Tests the exclusive item bitvector for a specific exclusive item"
        " effect.\n\nr0: the effects bitvector to test\nr1: exclusive item effect"
        " ID\nreturn: bool",
    )

    ApplyGummiBoostsGroundMode = Symbol(
        None,
        None,
        None,
        "Applies the IQ boosts from eating a Gummi to the target monster.\n\nr0:"
        " Pointer to something\nr1: Pointer to something\nr2: Pointer to something\nr3:"
        " Pointer to something\nstack[0]: ?\nstack[1]: ?\nstack[2]: Pointer to a buffer"
        " to store some result into",
    )

    GetMoveTargetAndRange = Symbol(
        [0x13810],
        [0x2013810],
        None,
        "Gets the move target-and-range field. See struct move_target_and_range in the"
        " C headers.\n\nr0: move pointer\nr1: AI flag (every move has two"
        " target-and-range fields, one for players and one for AI)\nreturn: move target"
        " and range",
    )

    GetMoveType = Symbol(
        None,
        None,
        None,
        "Gets the type of a move\n\nr0: Pointer to move data\nreturn: Type of the move",
    )

    GetMoveAiWeight = Symbol(
        None,
        None,
        None,
        "Gets the AI weight of a move\n\nr0: Pointer to move data\nreturn: AI weight of"
        " the move",
    )

    GetMoveBasePower = Symbol(
        [0x1399C],
        [0x201399C],
        None,
        "Gets the base power of a move from the move data table.\n\nr0: move"
        " pointer\nreturn: base power",
    )

    GetMoveAccuracyOrAiChance = Symbol(
        None,
        None,
        None,
        "Gets one of the two accuracy values of a move or its"
        " ai_condition_random_chance field.\n\nr0: Move pointer\nr1: 0 to get the"
        " move's first accuracy1 field, 1 to get its accuracy2, 2 to get its"
        " ai_condition_random_chance.\nreturn: Move's accuracy1, accuracy2 or"
        " ai_condition_random_chance",
    )

    GetMaxPp = Symbol(
        [0x13A20],
        [0x2013A20],
        None,
        "Gets the maximum PP for a given move.\n\nr0: move pointer\nreturn: max PP for"
        " the given move, capped at 99",
    )

    GetMoveCritChance = Symbol(
        [0x13AE0],
        [0x2013AE0],
        None,
        "Gets the critical hit chance of a move.\n\nr0: move pointer\nreturn: base"
        " power",
    )

    IsMoveRangeString19 = Symbol(
        None,
        None,
        None,
        "Returns whether a move's range string is 19 ('User').\n\nr0: Move"
        " pointer\nreturn: True if the move's range string field has a value of 19.",
    )

    IsRecoilMove = Symbol(
        None,
        None,
        None,
        "Checks if the given move is a recoil move (affected by Reckless).\n\nr0: move"
        " ID\nreturn: bool",
    )

    IsPunchMove = Symbol(
        None,
        None,
        None,
        "Checks if the given move is a punch move (affected by Iron Fist).\n\nr0: move"
        " ID\nreturn: bool",
    )

    GetMoveCategory = Symbol(
        [0x15198],
        [0x2015198],
        None,
        "Gets a move's category (physical, special, status).\n\nr0: move ID\nreturn:"
        " move category enum",
    )

    LoadWteFromRom = Symbol(
        [0x1DEA4],
        [0x201DEA4],
        None,
        "Loads a SIR0-wrapped WTE file from ROM, and returns a handle to it\n\nr0:"
        " [output] pointer to wte handle\nr1: file path string\nr2: load file flags",
    )

    LoadWteFromFileDirectory = Symbol(
        [0x1DF1C],
        [0x201DF1C],
        None,
        "Loads a SIR0-wrapped WTE file from a file directory, and returns a handle to"
        " it\n\nr0: [output] pointer to wte handle\nr1: file directory id\nr2: file"
        " index\nr3: malloc flags",
    )

    UnloadWte = Symbol(
        [0x1DF70],
        [0x201DF70],
        None,
        "Frees the buffer used to store the WTE data in the handle, and sets both"
        " pointers to null\n\nr0: pointer to wte handle",
    )

    HandleSir0Translation = Symbol(
        [0x1F50C],
        [0x201F50C],
        None,
        "Translates the offsets in a SIR0 file into NDS memory addresses, changes the"
        " magic number to SirO (opened), and returns a pointer to the first pointer"
        " specified in the SIR0 header (beginning of the data).\n\nr0: [output] double"
        " pointer to beginning of data\nr1: pointer to source file buffer",
    )

    HandleSir0TranslationVeneer = Symbol(
        None,
        None,
        None,
        "Likely a linker-generated veneer for HandleSir0Translation.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nr0:"
        " [output] double pointer to beginning of data\nr1: pointer to source file"
        " buffer",
    )

    GetLanguageType = Symbol(
        [0x205F8],
        [0x20205F8],
        None,
        "Gets the language type.\n\nThis is the value backing the special LANGUAGE_TYPE"
        " script variable.\n\nreturn: language type",
    )

    GetLanguage = Symbol(
        [0x20608],
        [0x2020608],
        None,
        "Gets the single-byte language ID of the current program.\n\nThe language ID"
        " appears to be used to index some global tables.\n\nreturn: language ID",
    )

    PreprocessString = Symbol(
        [0x22440],
        [0x2022440],
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
        [0x25150],
        [0x2025150],
        None,
        "A simple implementation of the strcpy(3) C library function.\n\nThis function"
        " was probably manually implemented by the developers. See Strcpy for what's"
        " probably the real libc function.\n\nr0: dest\nr1: src",
    )

    StrncpySimple = Symbol(
        [0x2516C],
        [0x202516C],
        None,
        "A simple implementation of the strncpy(3) C library function.\n\nThis function"
        " was probably manually implemented by the developers. See Strncpy for what's"
        " probably the real libc function.\n\nr0: dest\nr1: src\nr2: n",
    )

    StringFromMessageId = Symbol(
        [0x258A4],
        [0x20258A4],
        None,
        "Gets the string corresponding to a given message ID.\n\nr0: message"
        " ID\nreturn: string from the string files with the given message ID",
    )

    SetScreenWindowsColor = Symbol(
        [0x27DC8],
        [0x2027DC8],
        None,
        "Sets the palette of the frames of windows in the specified screen\n\nr0:"
        " palette index\nr1: is upper screen",
    )

    SetBothScreensWindowsColor = Symbol(
        [0x27DE0],
        [0x2027DE0],
        None,
        "Sets the palette of the frames of windows in both screens\n\nr0: palette"
        " index",
    )

    GetNotifyNote = Symbol(
        None, None, None, "Returns the current value of NOTIFY_NOTE.\n\nreturn: bool"
    )

    SetNotifyNote = Symbol(
        None, None, None, "Sets NOTIFY_NOTE to the given value.\n\nr0: bool"
    )

    InitMainTeamAfterQuiz = Symbol(
        [0x48B30],
        [0x2048B30],
        None,
        "Implements SPECIAL_PROC_INIT_MAIN_TEAM_AFTER_QUIZ (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x3 = Symbol(
        [0x48D78],
        [0x2048D78],
        None,
        "Implements SPECIAL_PROC_0x3 (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x4 = Symbol(
        [0x48DF0],
        [0x2048DF0],
        None,
        "Implements SPECIAL_PROC_0x4 (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    NoteSaveBase = Symbol(
        [0x492F0],
        [0x20492F0],
        None,
        "Probably related to saving or quicksaving?\n\nThis function prints the debug"
        " message 'NoteSave Base %d %d' with some values. It's also the only place"
        " where GetRngSeed is called.\n\nr0: possibly a flag/code that controls the"
        " type of save file to generate?\nothers: ?\nreturn: status code",
    )

    NoteLoadBase = Symbol(
        [0x496DC],
        [0x20496DC],
        None,
        "Probably related to loading a save file or quicksave?\n\nThis function prints"
        " the debug message 'NoteLoad Base %d' with some value. It's also the only"
        " place where SetRngSeed is called.\n\nreturn: status code",
    )

    GetGameMode = Symbol(
        None, None, None, "Gets the value of GAME_MODE.\n\nreturn: game mode"
    )

    InitScriptVariableValues = Symbol(
        [0x4B3B4],
        [0x204B3B4],
        None,
        "Initialize the script variable values table (SCRIPT_VARS_VALUES).\n\nThe whole"
        " table is first zero-initialized. Then, all script variable values are first"
        " initialized to their defaults, after which some of them are overwritten with"
        " other hard-coded values.\n\nNo params.",
    )

    InitEventFlagScriptVars = Symbol(
        None,
        None,
        None,
        "Initializes an assortment of event flag script variables (see the code for an"
        " exhaustive list).\n\nNo params.",
    )

    ZinitScriptVariable = Symbol(
        [0x4B794],
        [0x204B794],
        None,
        "Zero-initialize the values of the given script variable.\n\nr0: pointer to the"
        " local variable table (only needed if id >= VAR_LOCAL0)\nr1: script"
        " variable ID",
    )

    LoadScriptVariableRaw = Symbol(
        [0x4B7FC],
        [0x204B7FC],
        None,
        "Loads a script variable descriptor for a given ID.\n\nr0: [output] script"
        " variable descriptor pointer\nr1: pointer to the local variable table (doesn't"
        " need to be valid; just controls the output value pointer)\nr2: script"
        " variable ID",
    )

    LoadScriptVariableValue = Symbol(
        [0x4B84C],
        [0x204B84C],
        None,
        "Loads the value of a script variable.\n\nr0: pointer to the local variable"
        " table (only needed if id >= VAR_LOCAL0)\nr1: script variable ID\nreturn:"
        " value",
    )

    LoadScriptVariableValueAtIndex = Symbol(
        [0x4B9D8],
        [0x204B9D8],
        None,
        "Loads the value of a script variable at some index (for script variables that"
        " are arrays).\n\nr0: pointer to the local variable table (only needed if id >="
        " VAR_LOCAL0)\nr1: script variable ID\nr2: value index for the given script"
        " var\nreturn: value",
    )

    SaveScriptVariableValue = Symbol(
        [0x4BB80],
        [0x204BB80],
        None,
        "Saves the given value to a script variable.\n\nr0: pointer to local variable"
        " table (only needed if id >= VAR_LOCAL0)\nr1: script variable ID\nr2: value to"
        " save",
    )

    SaveScriptVariableValueAtIndex = Symbol(
        [0x4BCE8],
        [0x204BCE8],
        None,
        "Saves the given value to a script variable at some index (for script variables"
        " that are arrays).\n\nr0: pointer to local variable table (only needed if id"
        " >= VAR_LOCAL0)\nr1: script variable ID\nr2: value index for the given script"
        " var\nr3: value to save",
    )

    LoadScriptVariableValueSum = Symbol(
        [0x4BE60],
        [0x204BE60],
        None,
        "Loads the sum of all values of a given script variable (for script variables"
        " that are arrays).\n\nr0: pointer to the local variable table (only needed if"
        " id >= VAR_LOCAL0)\nr1: script variable ID\nreturn: sum of values",
    )

    LoadScriptVariableValueBytes = Symbol(
        [0x4BEC4],
        [0x204BEC4],
        None,
        "Loads some number of bytes from the value of a given script variable.\n\nr0:"
        " script variable ID\nr1: [output] script variable value bytes\nr2: number of"
        " bytes to load",
    )

    SaveScriptVariableValueBytes = Symbol(
        [0x4BF2C],
        [0x204BF2C],
        None,
        "Saves some number of bytes to the given script variable.\n\nr0: script"
        " variable ID\nr1: bytes to save\nr2: number of bytes",
    )

    ScriptVariablesEqual = Symbol(
        [0x4BF78],
        [0x204BF78],
        None,
        "Checks if two script variables have equal values. For arrays, compares"
        " elementwise for the length of the first variable.\n\nr0: pointer to the local"
        " variable table (only needed if id >= VAR_LOCAL0)\nr1: script variable ID"
        " 1\nr2: script variable ID 2\nreturn: true if values are equal, false"
        " otherwise",
    )

    EventFlagBackup = Symbol(
        [0x4C544],
        [0x204C544],
        None,
        "Saves event flag script variables (see the code for an exhaustive list) to"
        " their respective BACKUP script variables, but only in certain game"
        " modes.\n\nThis function prints the debug string 'EventFlag BackupGameMode %d'"
        " with the game mode.\n\nNo params.",
    )

    DumpScriptVariableValues = Symbol(
        [0x4C768],
        [0x204C768],
        None,
        "Runs EventFlagBackup, then copies the script variable values table"
        " (SCRIPT_VARS_VALUES) to the given pointer.\n\nr0: destination pointer for the"
        " data dump\nreturn: always 1",
    )

    RestoreScriptVariableValues = Symbol(
        [0x4C790],
        [0x204C790],
        None,
        "Restores the script variable values table (SCRIPT_VARS_VALUES) with the given"
        " data. The source data is assumed to be exactly 1024 bytes in length.\n\nr0:"
        " raw data to copy to the values table\nreturn: whether the restored value for"
        " VAR_VERSION is equal to its default value",
    )

    InitScenarioScriptVars = Symbol(
        [0x4C7E8],
        [0x204C7E8],
        None,
        "Initializes most of the SCENARIO_* script variables (except"
        " SCENARIO_TALK_BIT_FLAG for some reason). Also initializes the PLAY_OLD_GAME"
        " variable.\n\nNo params.",
    )

    SetScenarioScriptVar = Symbol(
        [0x4C978],
        [0x204C978],
        None,
        "Sets the given SCENARIO_* script variable with a given pair of values [val0,"
        " val1].\n\nIn the special case when the ID is VAR_SCENARIO_MAIN, and the set"
        " value is different from the old one, the REQUEST_CLEAR_COUNT script variable"
        " will be set to 0.\n\nr0: script variable ID\nr1: val0\nr2: val1",
    )

    GetSpecialEpisodeType = Symbol(
        [0x4CC4C],
        [0x204CC4C],
        None,
        "Gets the special episode type from the SPECIAL_EPISODE_TYPE script"
        " variable.\n\nreturn: special episode type",
    )

    ScenarioFlagBackup = Symbol(
        [0x4D018],
        [0x204D018],
        None,
        "Saves scenario flag script variables (SCENARIO_SELECT, SCENARIO_MAIN_BIT_FLAG)"
        " to their respective BACKUP script variables, but only in certain game"
        " modes.\n\nThis function prints the debug string 'ScenarioFlag BackupGameMode"
        " %d' with the game mode.\n\nNo params.",
    )

    InitWorldMapScriptVars = Symbol(
        [0x4D0E8],
        [0x204D0E8],
        None,
        "Initializes the WORLD_MAP_* script variable values (IDs 0x55-0x57).\n\nNo"
        " params.",
    )

    InitDungeonListScriptVars = Symbol(
        [0x4D1F0],
        [0x204D1F0],
        None,
        "Initializes the DUNGEON_*_LIST script variable values (IDs 0x4f-0x54).\n\nNo"
        " params.",
    )

    SetDungeonTipShown = Symbol(
        None,
        None,
        None,
        "Marks a dungeon tip as already shown to the player\n\nr0: Dungeon tip ID",
    )

    GetDungeonTipShown = Symbol(
        None,
        None,
        None,
        "Checks if a dungeon tip has already been shown before or not.\n\nr0: Dungeon"
        " tip ID\nreturn: True if the tip has been shown before, false otherwise.",
    )

    MonsterSpawnsEnabled = Symbol(
        [0x4D6C0],
        [0x204D6C0],
        None,
        "Always returns true.\n\nThis function seems to be a debug switch that the"
        " developers may have used to disable the random enemy spawn. \nIf it returned"
        " false, the call to SpawnMonster inside TrySpawnMonsterAndTickSpawnCounter"
        " would not be executed.\n\nreturn: bool (always true)",
    )

    SetAdventureLogStructLocation = Symbol(
        [0x4FD70],
        [0x204FD70],
        None,
        "Sets the location of the adventure log struct in memory.\n\nSets it in a"
        " static memory location (At 0x22AB69C [US], 0x22ABFDC [EU], 0x22ACE58"
        " [JP])\n\nNo params.",
    )

    SetAdventureLogDungeonFloor = Symbol(
        [0x4FD88],
        [0x204FD88],
        None,
        "Sets the current dungeon floor pair.\n\nr0: struct dungeon_floor_pair",
    )

    GetAdventureLogDungeonFloor = Symbol(
        [0x4FDA8],
        [0x204FDA8],
        None,
        "Gets the current dungeon floor pair.\n\nreturn: struct dungeon_floor_pair",
    )

    ClearAdventureLogStruct = Symbol(
        [0x4FDBC],
        [0x204FDBC],
        None,
        "Clears the adventure log structure.\n\nNo params.",
    )

    SetAdventureLogCompleted = Symbol(
        [0x4FEE8],
        [0x204FEE8],
        None,
        "Marks one of the adventure log entry as completed.\n\nr0: entry ID",
    )

    IsAdventureLogNotEmpty = Symbol(
        [0x4FF10],
        [0x204FF10],
        None,
        "Checks if at least one of the adventure log entry is completed.\n\nreturn:"
        " bool",
    )

    GetAdventureLogCompleted = Symbol(
        [0x4FF48],
        [0x204FF48],
        None,
        "Checks if one adventure log entry is completed.\n\nr0: entry ID\nreturn: bool",
    )

    IncrementNbDungeonsCleared = Symbol(
        [0x4FF74],
        [0x204FF74],
        None,
        "Increments by 1 the number of dungeons cleared.\n\nImplements"
        " SPECIAL_PROC_0x3A (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    GetNbDungeonsCleared = Symbol(
        [0x4FFB8],
        [0x204FFB8],
        None,
        "Gets the number of dungeons cleared.\n\nreturn: the number of dungeons"
        " cleared",
    )

    IncrementNbFriendRescues = Symbol(
        [0x4FFCC],
        [0x204FFCC],
        None,
        "Increments by 1 the number of successful friend rescues.\n\nNo params.",
    )

    GetNbFriendRescues = Symbol(
        [0x50014],
        [0x2050014],
        None,
        "Gets the number of successful friend rescues.\n\nreturn: the number of"
        " successful friend rescues",
    )

    IncrementNbEvolutions = Symbol(
        [0x50028],
        [0x2050028],
        None,
        "Increments by 1 the number of evolutions.\n\nNo params.",
    )

    GetNbEvolutions = Symbol(
        [0x50070],
        [0x2050070],
        None,
        "Gets the number of evolutions.\n\nreturn: the number of evolutions",
    )

    IncrementNbSteals = Symbol(
        [0x50084],
        [0x2050084],
        None,
        "Leftover from Time & Darkness. Does not do anything.\n\nCalls to this matches"
        " the ones for incrementing the number of successful steals in Time &"
        " Darkness.\n\nNo params.",
    )

    IncrementNbEggsHatched = Symbol(
        [0x50088],
        [0x2050088],
        None,
        "Increments by 1 the number of eggs hatched.\n\nNo params.",
    )

    GetNbEggsHatched = Symbol(
        [0x500C4],
        [0x20500C4],
        None,
        "Gets the number of eggs hatched.\n\nreturn: the number of eggs hatched",
    )

    GetNbPokemonJoined = Symbol(
        [0x500D8],
        [0x20500D8],
        None,
        "Gets the number of different pokémon that joined.\n\nreturn: the number of"
        " different pokémon that joined",
    )

    GetNbMovesLearned = Symbol(
        [0x500EC],
        [0x20500EC],
        None,
        "Gets the number of different moves learned.\n\nreturn: the number of different"
        " moves learned",
    )

    SetVictoriesOnOneFloor = Symbol(
        [0x50100],
        [0x2050100],
        None,
        "Sets the record of victories on one floor.\n\nr0: the new record of victories",
    )

    GetVictoriesOnOneFloor = Symbol(
        [0x50134],
        [0x2050134],
        None,
        "Gets the record of victories on one floor.\n\nreturn: the record of victories",
    )

    SetPokemonJoined = Symbol(
        [0x50148], [0x2050148], None, "Marks one pokémon as joined.\n\nr0: monster ID"
    )

    SetPokemonBattled = Symbol(
        [0x501A4], [0x20501A4], None, "Marks one pokémon as battled.\n\nr0: monster ID"
    )

    GetNbPokemonBattled = Symbol(
        [0x50200],
        [0x2050200],
        None,
        "Gets the number of different pokémon that battled against you.\n\nreturn: the"
        " number of different pokémon that battled against you",
    )

    IncrementNbBigTreasureWins = Symbol(
        [0x50214],
        [0x2050214],
        None,
        "Increments by 1 the number of big treasure wins.\n\nImplements"
        " SPECIAL_PROC_0x3B (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    SetNbBigTreasureWins = Symbol(
        [0x50234],
        [0x2050234],
        None,
        "Sets the number of big treasure wins.\n\nr0: the new number of big treasure"
        " wins",
    )

    GetNbBigTreasureWins = Symbol(
        [0x5026C],
        [0x205026C],
        None,
        "Gets the number of big treasure wins.\n\nreturn: the number of big treasure"
        " wins",
    )

    SetNbRecycled = Symbol(
        [0x50280],
        [0x2050280],
        None,
        "Sets the number of items recycled.\n\nr0: the new number of items recycled",
    )

    GetNbRecycled = Symbol(
        [0x502B8],
        [0x20502B8],
        None,
        "Gets the number of items recycled.\n\nreturn: the number of items recycled",
    )

    IncrementNbSkyGiftsSent = Symbol(
        [0x502CC],
        [0x20502CC],
        None,
        "Increments by 1 the number of sky gifts sent.\n\nImplements"
        " SPECIAL_PROC_SEND_SKY_GIFT_TO_GUILDMASTER (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    SetNbSkyGiftsSent = Symbol(
        [0x502EC],
        [0x20502EC],
        None,
        "Sets the number of Sky Gifts sent.\n\nreturn: the number of Sky Gifts sent",
    )

    GetNbSkyGiftsSent = Symbol(
        [0x50324],
        [0x2050324],
        None,
        "Gets the number of Sky Gifts sent.\n\nreturn: the number of Sky Gifts sent",
    )

    ComputeSpecialCounters = Symbol(
        [0x50338],
        [0x2050338],
        None,
        "Computes the counters from the bit fields in the adventure log, as they are"
        " not updated automatically when bit fields are altered.\n\nAffects"
        " GetNbPokemonJoined, GetNbMovesLearned, GetNbPokemonBattled and"
        " GetNbItemAcquired.\n\nNo params.",
    )

    RecruitSpecialPokemonLog = Symbol(
        [0x50590],
        [0x2050590],
        None,
        "Marks a specified special pokémon as recruited in the adventure log.\n\nr0:"
        " monster ID",
    )

    IncrementNbFainted = Symbol(
        [0x505FC],
        [0x20505FC],
        None,
        "Increments by 1 the number of times you fainted.\n\nNo params.",
    )

    GetNbFainted = Symbol(
        [0x50638],
        [0x2050638],
        None,
        "Gets the number of times you fainted.\n\nreturn: the number of times you"
        " fainted",
    )

    SetItemAcquired = Symbol(
        [0x5064C],
        [0x205064C],
        None,
        "Marks one specific item as acquired.\n\nr0: item ID",
    )

    GetNbItemAcquired = Symbol(
        [0x50718],
        [0x2050718],
        None,
        "Gets the number of items acquired.\n\nreturn: the number of items acquired",
    )

    SetChallengeLetterCleared = Symbol(
        [0x5076C],
        [0x205076C],
        None,
        "Sets a challenge letter as cleared.\n\nr0: challenge ID",
    )

    GetSentryDutyGamePoints = Symbol(
        [0x507F0],
        [0x20507F0],
        None,
        "Gets the points for the associated rank in the footprints minigame.\n\nr0: the"
        " rank (range 0-4, 1st to 5th)\nreturn: points",
    )

    SetSentryDutyGamePoints = Symbol(
        [0x50808],
        [0x2050808],
        None,
        "Sets a new record in the footprints minigame.\n\nr0: points\nreturn: the rank"
        " (range 0-4, 1st to 5th; -1 if out of ranking)",
    )

    SubFixedPoint = Symbol(
        [0x51260],
        [0x2051260],
        None,
        "Compute the subtraction of two decimal fixed-point numbers (16 fraction"
        " bits).\n\nFloats are in the format {16-bit integer part, 16-bit thousandths},"
        " where the integer part is the lower word. Probably used primarily for"
        " belly.\n\nr0: float\nr1: decrement\nreturn: max(float - decrement, 0)",
    )

    BinToDecFixedPoint = Symbol(
        [0x51370],
        [0x2051370],
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
        [0x513B4],
        [0x20513B4],
        None,
        "Compute the ceiling of a decimal fixed-point number (16 fraction"
        " bits).\n\nFloats are in the format {16-bit integer part, 16-bit thousandths},"
        " where the integer part is the lower word. Probably used primarily for"
        " belly.\n\nr0: float\nreturn: ceil(float)",
    )

    DungeonGoesUp = Symbol(
        [0x515D8],
        [0x20515D8],
        None,
        "Returns whether the specified dungeon is considered as going upward or"
        " not\n\nr0: dungeon id\nreturn: bool",
    )

    GetMaxRescueAttempts = Symbol(
        None,
        None,
        None,
        "Returns the maximum rescue attempts allowed in the specified dungeon.\n\nr0:"
        " dungeon id\nreturn: Max rescue attempts, or -1 if rescues are disabled.",
    )

    JoinedAtRangeCheck = Symbol(
        None,
        None,
        None,
        "Returns whether a certain joined_at field value is between"
        " dungeon_id::DUNGEON_JOINED_AT_BIDOOF and"
        " dungeon_id::DUNGEON_DUMMY_0xE3.\n\nr0: joined_at id\nreturn: bool",
    )

    JoinedAtRangeCheck2 = Symbol(
        None,
        None,
        None,
        "Returns whether a certain joined_at field value is equal to"
        " dungeon_id::DUNGEON_BEACH or is between dungeon_id::DUNGEON_DUMMY_0xEC and"
        " dungeon_id::DUNGEON_DUMMY_0xF0.\n\nr0: joined_at id\nreturn: bool",
    )

    GetMonsterGender = Symbol(
        None,
        None,
        None,
        "Returns the gender field of a monster given its ID.\n\nr0: monster id\nreturn:"
        " monster gender",
    )

    GetSpriteSize = Symbol(
        None,
        None,
        None,
        "Returns the sprite size of the specified monster. If the size is between 1 and"
        " 6, 6 will be returned.\n\nr0: monster id\nreturn: sprite size",
    )

    GetSpriteFileSize = Symbol(
        None,
        None,
        None,
        "Returns the sprite file size of the specified monster.\n\nr0: monster"
        " id\nreturn: sprite file size",
    )

    GetCanMoveFlag = Symbol(
        None,
        None,
        None,
        "Returns the flag that determines if a monster can move in dungeons.\n\nr0:"
        " Monster ID\nreturn: 'Can move' flag",
    )

    GetMonsterPreEvolution = Symbol(
        None,
        None,
        None,
        "Returns the pre-evolution id of a monster given its ID.\n\nr0: monster"
        " id\nreturn: ID of the monster that evolves into the one specified in r0",
    )

    GetEvolutions = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Returns the monster ID of the specified monster spawn entry\n\nr0: Pointer to"
        " the monster spawn entry\nreturn: monster_spawn_entry::id",
    )

    GetMonsterLevelFromSpawnEntry = Symbol(
        [0x547F0],
        [0x20547F0],
        None,
        "Returns the level of the specified monster spawn entry.\n\nr0: pointer to the"
        " monster spawn entry\nreturn: uint8_t",
    )

    GetMonsterGenderVeneer = Symbol(
        None,
        None,
        None,
        "Likely a linker-generated veneer for GetMonsterGender.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nr0:"
        " monster id\nreturn: monster gender",
    )

    IsUnown = Symbol(
        [0x54DC0],
        [0x2054DC0],
        None,
        "Checks if a monster ID is an Unown.\n\nr0: monster ID\nreturn: bool",
    )

    IsShaymin = Symbol(
        [0x54DDC],
        [0x2054DDC],
        None,
        "Checks if a monster ID is a Shaymin form.\n\nr0: monster ID\nreturn: bool",
    )

    IsCastform = Symbol(
        [0x54E0C],
        [0x2054E0C],
        None,
        "Checks if a monster ID is a Castform form.\n\nr0: monster ID\nreturn: bool",
    )

    IsCherrim = Symbol(
        [0x54E64],
        [0x2054E64],
        None,
        "Checks if a monster ID is a Cherrim form.\n\nr0: monster ID\nreturn: bool",
    )

    IsDeoxys = Symbol(
        [0x54EAC],
        [0x2054EAC],
        None,
        "Checks if a monster ID is a Deoxys form.\n\nr0: monster ID\nreturn: bool",
    )

    IsMonsterOnTeam = Symbol(
        [0x55480],
        [0x2055480],
        None,
        "Checks if a given monster is on the exploration team (not necessarily the"
        " active party)?\n\nr0: monster ID\nr1: ?\nreturn: bool",
    )

    CheckTeamMemberField8 = Symbol(
        None,
        None,
        None,
        "Checks if a value obtained from team_member::field_0x8 is equal to certain"
        " values.\n\nThis is known to return true for some or all of the guest"
        " monsters.\n\nr0: Value read from team_member::field_0x8\nreturn: True if the"
        " value is equal to 0x55AA or 0x5AA5",
    )

    GetTeamMemberData = Symbol(
        None,
        None,
        None,
        "Returns a struct containing information about a team member.\n\nr0:"
        " Index\nreturn: Pointer to struct containing team member information",
    )

    SetTeamSetupHeroAndPartnerOnly = Symbol(
        [0x56D68],
        [0x2056D68],
        None,
        "Implements SPECIAL_PROC_SET_TEAM_SETUP_HERO_AND_PARTNER_ONLY (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    SetTeamSetupHeroOnly = Symbol(
        [0x56E48],
        [0x2056E48],
        None,
        "Implements SPECIAL_PROC_SET_TEAM_SETUP_HERO_ONLY (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    GetPartyMembers = Symbol(
        [0x56FB4],
        [0x2056FB4],
        None,
        "Appears to get the team's active party members. Implements most of"
        " SPECIAL_PROC_IS_TEAM_SETUP_SOLO (see ScriptSpecialProcessCall).\n\nr0:"
        " [output] Array of 4 2-byte values (they seem to be indexes of some sort)"
        " describing each party member, which will be filled in by the function. The"
        " input can be a null pointer if the party members aren't needed\nreturn:"
        " Number of party members",
    )

    IqSkillFlagTest = Symbol(
        [0x59200],
        [0x2059200],
        None,
        "Tests whether an IQ skill with a given ID is active.\n\nr0: IQ skill bitvector"
        " to test\nr1: IQ skill ID\nreturn: bool",
    )

    GetExplorerMazeMonster = Symbol(
        None,
        None,
        None,
        "Returns the data of a monster sent into the Explorer Dojo using the 'exchange"
        " teams' option.\n\nr0: Entry number (0-3)\nreturn: Ground monster data of the"
        " specified entry",
    )

    GetSosMailCount = Symbol(
        [0x5BC7C],
        [0x205BC7C],
        None,
        "Implements SPECIAL_PROC_GET_SOS_MAIL_COUNT (see"
        " ScriptSpecialProcessCall).\n\nr0: ?\nr1: some flag?\nreturn: SOS mail count",
    )

    DungeonRequestsDone = Symbol(
        [0x5F0A4],
        [0x205F0A4],
        None,
        "Seems to return the number of missions completed.\n\nPart of the"
        " implementation for SPECIAL_PROC_DUNGEON_HAD_REQUEST_DONE (see"
        " ScriptSpecialProcessCall).\n\nr0: ?\nr1: some flag?\nreturn: number of"
        " missions completed",
    )

    DungeonRequestsDoneWrapper = Symbol(
        None,
        None,
        None,
        "Calls DungeonRequestsDone with the second argument set to false.\n\nr0:"
        " ?\nreturn: number of mission completed",
    )

    AnyDungeonRequestsDone = Symbol(
        [0x5F120],
        [0x205F120],
        None,
        "Calls DungeonRequestsDone with the second argument set to true, and converts"
        " the integer output to a boolean.\n\nr0: ?\nreturn: bool: whether the number"
        " of missions completed is greater than 0",
    )

    ScriptSpecialProcess0x3D = Symbol(
        [0x65E38],
        [0x2065E38],
        None,
        "Implements SPECIAL_PROC_0x3D (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x3E = Symbol(
        [0x65E48],
        [0x2065E48],
        None,
        "Implements SPECIAL_PROC_0x3E (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x17 = Symbol(
        [0x65F30],
        [0x2065F30],
        None,
        "Implements SPECIAL_PROC_0x17 (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ItemAtTableIdx = Symbol(
        [0x65FE0],
        [0x2065FE0],
        None,
        "Gets info about the item at a given item table (not sure what this table"
        " is...) index.\n\nUsed by SPECIAL_PROC_COUNT_TABLE_ITEM_TYPE_IN_BAG and"
        " friends (see ScriptSpecialProcessCall).\n\nr0: table index\nr1: [output]"
        " pointer to an owned_item",
    )

    WaitForInterrupt = Symbol(
        [0x7BF18],
        [0x207BF18],
        None,
        "Presumably blocks until the program receives an interrupt.\n\nThis just calls"
        " (in Ghidra terminology) coproc_moveto_Wait_for_interrupt(0). See"
        " https://en.wikipedia.org/wiki/ARM_architecture_family#Coprocessors.\n\nNo"
        " params.",
    )

    FileInit = Symbol(
        [0x7F6CC],
        [0x207F6CC],
        None,
        "Initializes a file_stream structure for file I/O.\n\nThis function must always"
        " be called before opening a file.\n\nr0: file_stream pointer",
    )

    Abs = Symbol(
        [0x86844],
        [0x2086844],
        None,
        "Takes the absolute value of an integer.\n\nr0: x\nreturn: abs(x)",
    )

    Mbtowc = Symbol(
        [0x874A4],
        [0x20874A4],
        None,
        "The mbtowc(3) C library function.\n\nr0: pwc\nr1: s\nr2: n\nreturn: number of"
        " consumed bytes, or -1 on failure",
    )

    TryAssignByte = Symbol(
        [0x874DC],
        [0x20874DC],
        None,
        "Assign a byte to the target of a pointer if the pointer is non-null.\n\nr0:"
        " pointer\nr1: value\nreturn: true on success, false on failure",
    )

    TryAssignByteWrapper = Symbol(
        [0x874F0],
        [0x20874F0],
        None,
        "Wrapper around TryAssignByte.\n\nAccesses the TryAssignByte function with a"
        " weird chain of pointer dereferences.\n\nr0: pointer\nr1: value\nreturn: true"
        " on success, false on failure",
    )

    Wcstombs = Symbol(
        [0x8750C],
        [0x208750C],
        None,
        "The wcstombs(3) C library function.\n\nr0: dest\nr1: src\nr2: n\nreturn:"
        " characters converted",
    )

    Memcpy = Symbol(
        [0x87584],
        [0x2087584],
        None,
        "The memcpy(3) C library function.\n\nr0: dest\nr1: src\nr2: n",
    )

    Memmove = Symbol(
        [0x875A4],
        [0x20875A4],
        None,
        "The memmove(3) C library function.\n\nThe implementation is nearly the same as"
        " Memcpy, but it copies bytes from back to front if src < dst.\n\nr0: dest\nr1:"
        " src\nr2: n",
    )

    Memset = Symbol(
        [0x875F0],
        [0x20875F0],
        None,
        "The memset(3) C library function.\n\nThis is just a wrapper around"
        " MemsetInternal that returns the pointer at the end.\n\nr0: s\nr1: c (int, but"
        " must be a single-byte value)\nr2: n\nreturn: s",
    )

    Memchr = Symbol(
        [0x87604],
        [0x2087604],
        None,
        "The memchr(3) C library function.\n\nr0: s\nr1: c\nr2: n\nreturn: pointer to"
        " first occurrence of c in s, or a null pointer if no match",
    )

    Memcmp = Symbol(
        [0x87630],
        [0x2087630],
        None,
        "The memcmp(3) C library function.\n\nr0: s1\nr1: s2\nr2: n\nreturn: comparison"
        " value",
    )

    MemsetInternal = Symbol(
        [0x87670],
        [0x2087670],
        None,
        "The actual memory-setting implementation for the memset(3) C library"
        " function.\n\nThis function is optimized to set bytes in 4-byte chunks for n"
        " >= 32, correctly handling any unaligned bytes at the front/back. In this"
        " case, it also further optimizes by unrolling a for loop to set 8 4-byte"
        " values at once (effectively a 32-byte chunk).\n\nr0: s\nr1: c (int, but must"
        " be a single-byte value)\nr2: n",
    )

    VsprintfInternalSlice = Symbol(
        [0x88F5C],
        [0x2088F5C],
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
        [0x89780],
        [0x2089780],
        None,
        "Best-effort append the given data to a slice. If the slice's capacity is"
        " reached, any remaining data will be truncated.\n\nr0: slice pointer\nr1:"
        " buffer of data to append\nr2: number of bytes in the data buffer\nreturn:"
        " true",
    )

    VsprintfInternal = Symbol(
        [0x897C4],
        [0x20897C4],
        None,
        "This is what implements Vsprintf. It's akin to __vsprintf_internal in the"
        " modern-day version of glibc (in fact, it's probably an older version of"
        " this).\n\nr0: str\nr1: maxlen (Vsprintf passes UINT32_MAX for this)\nr2:"
        " format\nr3: ap\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    Vsprintf = Symbol(
        [0x8982C],
        [0x208982C],
        None,
        "The vsprintf(3) C library function.\n\nr0: str\nr1: format\nr2: ap\nreturn:"
        " number of characters printed, excluding the null-terminator",
    )

    Snprintf = Symbol(
        [0x89844],
        [0x2089844],
        None,
        "The snprintf(3) C library function.\n\nThis calls VsprintfInternal directly,"
        " so it's presumably the real snprintf.\n\nr0: str\nr1: n\nr2: format\n...:"
        " variadic\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    Sprintf = Symbol(
        [0x8986C],
        [0x208986C],
        None,
        "The sprintf(3) C library function.\n\nThis calls VsprintfInternal directly, so"
        " it's presumably the real sprintf.\n\nr0: str\nr1: format\n...:"
        " variadic\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    Strlen = Symbol(
        [0x89960],
        [0x2089960],
        None,
        "The strlen(3) C library function.\n\nr0: s\nreturn: length of s",
    )

    Strcpy = Symbol(
        [0x8997C],
        [0x208997C],
        None,
        "The strcpy(3) C library function.\n\nThis function is optimized to copy"
        " characters in aligned 4-byte chunks if possible, correctly handling any"
        " unaligned bytes at the front/back.\n\nr0: dest\nr1: src",
    )

    Strncpy = Symbol(
        [0x89A44],
        [0x2089A44],
        None,
        "The strncpy(3) C library function.\n\nr0: dest\nr1: src\nr2: n",
    )

    Strcat = Symbol(
        [0x89A94],
        [0x2089A94],
        None,
        "The strcat(3) C library function.\n\nr0: dest\nr1: src",
    )

    Strncat = Symbol(
        [0x89AC4],
        [0x2089AC4],
        None,
        "The strncat(3) C library function.\n\nr0: dest\nr1: src\nr2: n",
    )

    Strcmp = Symbol(
        [0x89B14],
        [0x2089B14],
        None,
        "The strcmp(3) C library function.\n\nSimilarly to Strcpy, this function is"
        " optimized to compare characters in aligned 4-byte chunks if possible.\n\nr0:"
        " s1\nr1: s2\nreturn: comparison value",
    )

    Strncmp = Symbol(
        [0x89C28],
        [0x2089C28],
        None,
        "The strncmp(3) C library function.\n\nr0: s1\nr1: s2\nr2: n\nreturn:"
        " comparison value",
    )

    Strchr = Symbol(
        [0x89C5C],
        [0x2089C5C],
        None,
        "The strchr(3) C library function.\n\nr0: string\nr1: c\nreturn: pointer to the"
        " located byte c, or null pointer if no match",
    )

    Strcspn = Symbol(
        [0x89C98],
        [0x2089C98],
        None,
        "The strcspn(3) C library function.\n\nr0: string\nr1: stopset\nreturn: offset"
        " of the first character in string within stopset",
    )

    Strstr = Symbol(
        [0x89D58],
        [0x2089D58],
        None,
        "The strstr(3) C library function.\n\nr0: haystack\nr1: needle\nreturn: pointer"
        " into haystack where needle starts, or null pointer if no match",
    )

    Wcslen = Symbol(
        [0x8B6D0],
        [0x208B6D0],
        None,
        "The wcslen(3) C library function.\n\nr0: ws\nreturn: length of ws",
    )

    AddFloat = Symbol(
        [0x8EFA0],
        [0x208EFA0],
        None,
        "This appears to be the libgcc implementation of __addsf3 (not sure which gcc"
        " version), which implements the addition operator for IEEE 754 floating-point"
        " numbers.\n\nr0: a\nr1: b\nreturn: a + b",
    )

    DivideFloat = Symbol(
        [0x8F51C],
        [0x208F51C],
        None,
        "This appears to be the libgcc implementation of __divsf3 (not sure which gcc"
        " version), which implements the division operator for IEEE 754 floating-point"
        " numbers.\n\nr0: dividend\nr1: divisor\nreturn: dividend / divisor",
    )

    FloatToDouble = Symbol(
        [0x8F8D4],
        [0x208F8D4],
        None,
        "This appears to be the libgcc implementation of __extendsfdf2 (not sure which"
        " gcc version), which implements the float to double cast operation for IEEE"
        " 754 floating-point numbers.\n\nr0: float\nreturn: (double)float",
    )

    FloatToInt = Symbol(
        [0x8F958],
        [0x208F958],
        None,
        "This appears to be the libgcc implementation of __fixsfsi (not sure which gcc"
        " version), which implements the float to int cast operation for IEEE 754"
        " floating-point numbers. The output saturates if the input is out of the"
        " representable range for the int type.\n\nr0: float\nreturn: (int)float",
    )

    IntToFloat = Symbol(
        [0x8F98C],
        [0x208F98C],
        None,
        "This appears to be the libgcc implementation of __floatsisf (not sure which"
        " gcc version), which implements the int to float cast operation for IEEE 754"
        " floating-point numbers.\n\nr0: int\nreturn: (float)int",
    )

    UIntToFloat = Symbol(
        [0x8F9D4],
        [0x208F9D4],
        None,
        "This appears to be the libgcc implementation of __floatunsisf (not sure which"
        " gcc version), which implements the unsigned int to float cast operation for"
        " IEEE 754 floating-point numbers.\n\nr0: uint\nreturn: (float)uint",
    )

    MultiplyFloat = Symbol(
        [0x8FA1C],
        [0x208FA1C],
        None,
        "This appears to be the libgcc implementation of __mulsf3 (not sure which gcc"
        " version), which implements the multiplication operator for IEEE 754"
        " floating-point numbers.",
    )

    Sqrtf = Symbol(
        [0x8FBFC],
        [0x208FBFC],
        None,
        "The sqrtf(3) C library function.\n\nr0: x\nreturn: sqrt(x)",
    )

    SubtractFloat = Symbol(
        [0x8FCEC],
        [0x208FCEC],
        None,
        "This appears to be the libgcc implementation of __subsf3 (not sure which gcc"
        " version), which implements the subtraction operator for IEEE 754"
        " floating-point numbers.\n\nr0: a\nr1: b\nreturn: a - b",
    )

    DivideInt = Symbol(
        [0x9018C],
        [0x209018C],
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
        [0x90398],
        [0x2090398],
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
        [0x903A0],
        [0x20903A0],
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


class JpArm9Data:
    JUICE_BAR_NECTAR_IQ_GAIN = Symbol(
        None, None, None, "IQ gain when ingesting nectar at the Juice Bar."
    )

    TEXT_SPEED = Symbol(None, None, None, "Controls text speed.")

    HERO_START_LEVEL = Symbol(None, None, None, "Starting level of the hero.")

    PARTNER_START_LEVEL = Symbol(None, None, None, "Starting level of the partner.")

    DEFAULT_MEMORY_ARENA_SIZE = Symbol(
        None,
        None,
        None,
        "Length in bytes of the default memory allocation arena, 1991680.",
    )

    AURA_BOW_ID_LAST = Symbol(None, None, None, "Highest item ID of the aura bows.")

    NUMBER_OF_ITEMS = Symbol(None, None, None, "Number of items in the game.")

    MAX_MONEY_CARRIED = Symbol(
        None, None, None, "Maximum amount of money the player can carry, 99999."
    )

    MAX_MONEY_STORED = Symbol(
        None,
        None,
        None,
        "Maximum amount of money the player can store in the Duskull Bank, 9999999.",
    )

    SCRIPT_VARS_VALUES_PTR = Symbol(
        None, None, None, "Hard-coded pointer to SCRIPT_VARS_VALUES."
    )

    MONSTER_ID_LIMIT = Symbol(
        None, None, None, "One more than the maximum valid monster ID (0x483)."
    )

    MAX_RECRUITABLE_TEAM_MEMBERS = Symbol(
        None,
        None,
        None,
        "555, appears to be the maximum number of members recruited to an exploration"
        " team, at least for the purposes of some checks that need to iterate over all"
        " team members.",
    )

    CART_REMOVED_IMG_DATA = Symbol(None, None, None, "")

    EXCLUSIVE_ITEM_STAT_BOOST_DATA = Symbol(
        None,
        None,
        None,
        "Contains stat boost effects for different exclusive item classes.\n\nEach"
        " 4-byte entry contains the boost data for (attack, special attack, defense,"
        " special defense), 1 byte each, for a specific exclusive item class, indexed"
        " according to the stat boost data index list.",
    )

    EXCLUSIVE_ITEM_ATTACK_BOOSTS = Symbol(
        None, None, None, "EXCLUSIVE_ITEM_STAT_BOOST_DATA, offset by 0"
    )

    EXCLUSIVE_ITEM_SPECIAL_ATTACK_BOOSTS = Symbol(
        None, None, None, "EXCLUSIVE_ITEM_STAT_BOOST_DATA, offset by 1"
    )

    EXCLUSIVE_ITEM_DEFENSE_BOOSTS = Symbol(
        None, None, None, "EXCLUSIVE_ITEM_STAT_BOOST_DATA, offset by 2"
    )

    EXCLUSIVE_ITEM_SPECIAL_DEFENSE_BOOSTS = Symbol(
        None, None, None, "EXCLUSIVE_ITEM_STAT_BOOST_DATA, offset by 3"
    )

    EXCLUSIVE_ITEM_EFFECT_DATA = Symbol(
        None,
        None,
        None,
        "Contains special effects for each exclusive item.\n\nEach entry is 2 bytes,"
        " with the first entry corresponding to the first exclusive item (Prism Ruff)."
        " The first byte is the exclusive item effect ID, and the second byte is an"
        " index into other data tables (related to the more generic stat boosting"
        " effects for specific monsters).",
    )

    EXCLUSIVE_ITEM_STAT_BOOST_DATA_INDEXES = Symbol(
        None, None, None, "EXCLUSIVE_ITEM_EFFECT_DATA, offset by 1"
    )

    RECOIL_MOVE_LIST = Symbol(
        None,
        None,
        None,
        "Null-terminated list of all the recoil moves, as 2-byte move IDs.\n\ntype:"
        " struct move_id_16[11]",
    )

    PUNCH_MOVE_LIST = Symbol(
        None,
        None,
        None,
        "Null-terminated list of all the punch moves, as 2-byte move IDs.\n\ntype:"
        " struct move_id_16[16]",
    )

    SCRIPT_VARS_LOCALS = Symbol(
        None,
        None,
        None,
        "List of special 'local' variables available to the script engine. There are 4"
        " 16-byte entries.\n\nEach entry has the same structure as an entry in"
        " SCRIPT_VARS.\n\ntype: struct script_local_var_table",
    )

    SCRIPT_VARS = Symbol(
        [0x9EC44],
        [0x209EC44],
        0x730,
        "List of predefined global variables that track game state, which are available"
        " to the script engine. There are 115 16-byte entries.\n\nThese variables"
        " underpin the various ExplorerScript global variables you can use in the"
        " SkyTemple SSB debugger.\n\ntype: struct script_var_table",
    )

    DUNGEON_DATA_LIST = Symbol(
        None,
        None,
        None,
        "Data about every dungeon in the game.\n\nThis is an array of 180 dungeon data"
        " list entry structs. Each entry is 4 bytes, and contains floor count"
        " information along with an index into the bulk of the dungeon's data in"
        " mappa_s.bin.\n\nSee the struct definitions and End45's dungeon data document"
        " for more info.\n\ntype: struct dungeon_data_list_entry[180]",
    )

    DUNGEON_RESTRICTIONS = Symbol(
        None,
        None,
        None,
        "Data related to dungeon restrictions for every dungeon in the game.\n\nThis is"
        " an array of 256 dungeon restriction structs. Each entry is 12 bytes, and"
        " contains information about restrictions within the given dungeon.\n\nSee the"
        " struct definitions and End45's dungeon data document for more info.\n\ntype:"
        " struct dungeon_restriction[256]",
    )

    SPECIAL_BAND_STAT_BOOST = Symbol(
        None, None, None, "Stat boost value for the Special Band."
    )

    MUNCH_BELT_STAT_BOOST = Symbol(
        None, None, None, "Stat boost value for the Munch Belt."
    )

    GUMMI_STAT_BOOST = Symbol(
        None,
        None,
        None,
        "Stat boost value if a stat boost occurs when eating normal Gummis.",
    )

    MIN_IQ_EXCLUSIVE_MOVE_USER = Symbol(None, None, None, "")

    WONDER_GUMMI_IQ_GAIN = Symbol(
        None, None, None, "IQ gain when ingesting wonder gummis."
    )

    AURA_BOW_STAT_BOOST = Symbol(
        None, None, None, "Stat boost value for the aura bows."
    )

    MIN_IQ_ITEM_MASTER = Symbol(None, None, None, "")

    DEF_SCARF_STAT_BOOST = Symbol(
        None, None, None, "Stat boost value for the Defense Scarf."
    )

    POWER_BAND_STAT_BOOST = Symbol(
        None, None, None, "Stat boost value for the Power Band."
    )

    WONDER_GUMMI_STAT_BOOST = Symbol(
        None,
        None,
        None,
        "Stat boost value if a stat boost occurs when eating Wonder Gummis.",
    )

    ZINC_BAND_STAT_BOOST = Symbol(
        None, None, None, "Stat boost value for the Zinc Band."
    )

    TACTICS_UNLOCK_LEVEL_TABLE = Symbol(None, None, None, "")

    OUTLAW_LEVEL_TABLE = Symbol(
        None,
        None,
        None,
        "Table of 2-byte outlaw levels for outlaw missions, indexed by mission rank.",
    )

    OUTLAW_MINION_LEVEL_TABLE = Symbol(
        None,
        None,
        None,
        "Table of 2-byte outlaw minion levels for outlaw hideout missions, indexed by"
        " mission rank.",
    )

    IQ_SKILL_RESTRICTIONS = Symbol(
        None,
        None,
        None,
        "Table of 2-byte values for each IQ skill that represent a group. IQ skills in"
        " the same group can not be enabled at the same time.",
    )

    SECONDARY_TERRAIN_TYPES = Symbol(
        None,
        None,
        None,
        "The type of secondary terrain for each dungeon in the game.\n\nThis is an"
        " array of 200 bytes. Each byte is an enum corresponding to one"
        " dungeon.\n\ntype: struct secondary_terrain_type_8[200]",
    )

    SENTRY_MINIGAME_DATA = Symbol(None, None, None, "")

    IQ_SKILLS = Symbol(
        None,
        None,
        None,
        "Table of 4-byte values for each IQ skill that represent the required IQ value"
        " to unlock a skill.",
    )

    IQ_GROUP_SKILLS = Symbol(None, None, None, "")

    IQ_GUMMI_GAIN_TABLE = Symbol(None, None, None, "")

    GUMMI_BELLY_RESTORE_TABLE = Symbol(None, None, None, "")

    BAG_CAPACITY_TABLE = Symbol(
        None,
        None,
        None,
        "Array of 4-byte integers containing the bag capacity for each bag level.",
    )

    SPECIAL_EPISODE_MAIN_CHARACTERS = Symbol(None, None, None, "")

    GUEST_MONSTER_DATA = Symbol(
        None,
        None,
        None,
        "Data for guest monsters that join you during certain story dungeons.\n\nArray"
        " of 18 36-byte entries.\n\nSee the struct definitions and End45's dungeon data"
        " document for more info.\n\ntype: struct guest_monster[18]",
    )

    RANK_UP_TABLE = Symbol(None, None, None, "")

    MONSTER_SPRITE_DATA = Symbol(None, None, None, "")

    MISSION_DUNGEON_UNLOCK_TABLE = Symbol(None, None, None, "")

    EVENTS = Symbol(
        [0xA6894],
        [0x20A6894],
        0x1470,
        "Table of levels for the script engine, in which scenes can take place. There"
        " are a version-dependent number of 12-byte entries.\n\ntype: struct"
        " script_level[length / 12]",
    )

    ENTITIES = Symbol(
        [0xA9438],
        [0x20A9438],
        0x1218,
        "Table of entities for the script engine, which can move around and do things"
        " within a scene. There are 386 12-byte entries.\n\ntype: struct"
        " script_entity[386]",
    )

    MAP_MARKER_PLACEMENTS = Symbol(
        None,
        None,
        None,
        "The map marker position of each dungeon on the Wonder Map.\n\nThis is an array"
        " of 310 map marker structs. Each entry is 8 bytes, and contains positional"
        " information about a dungeon on the map.\n\nSee the struct definitions and"
        " End45's dungeon data document for more info.\n\ntype: struct map_marker[310]",
    )

    MEMORY_ALLOCATION_ARENA_GETTERS = Symbol(
        None,
        None,
        None,
        "Functions to get the desired memory arena for allocating and freeing heap"
        " memory.\n\ntype: struct mem_arena_getters",
    )

    PRNG_SEQUENCE_NUM = Symbol(
        None,
        None,
        None,
        "[Runtime] The current PRNG sequence number for the general-purpose PRNG. See"
        " Rand16Bit for more information on how the general-purpose PRNG works.",
    )

    LOADED_OVERLAY_GROUP_0 = Symbol(
        None,
        None,
        None,
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
        None,
        None,
        None,
        "[Runtime] The overlay group ID of the overlay currently loaded in slot 1. A"
        " group ID of 0 denotes no overlay.\n\nOverlay group IDs that can be loaded in"
        " slot 1:\n- 0x4 (overlay 1)\n- 0x5 (overlay 2)\n- 0xD (overlay 11)\n- 0xE"
        " (overlay 29)\n- 0xF (overlay 34)\n\ntype: enum overlay_group_id",
    )

    LOADED_OVERLAY_GROUP_2 = Symbol(
        None,
        None,
        None,
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
        None,
        None,
        None,
        "List of pointers to path strings to all known pack files.\nThe game uses this"
        " table to load its resources when launching dungeon mode.\n\ntype: char*[6]",
    )

    GAME_STATE_VALUES = Symbol(None, None, None, "[Runtime]")

    DUNGEON_MOVE_TABLES = Symbol(
        None,
        None,
        None,
        "[Runtime] Seems to be some sort of region (a table of tables?) that holds"
        " pointers to various important tables related to moves.",
    )

    MOVE_DATA_TABLE_PTR = Symbol(
        None,
        None,
        None,
        "[Runtime] Points to the contents of the move data table loaded from"
        " waza_p.bin\n\ntype: struct move_data_table*",
    )

    LANGUAGE_INFO_DATA = Symbol(None, None, None, "[Runtime]")

    NOTIFY_NOTE = Symbol(
        None,
        None,
        None,
        "[Runtime] Flag related to saving and loading state?\n\ntype: bool",
    )

    DEFAULT_HERO_ID = Symbol(
        None,
        None,
        None,
        "The default monster ID for the hero (0x4: Charmander)\n\ntype: struct"
        " monster_id_16",
    )

    DEFAULT_PARTNER_ID = Symbol(
        None,
        None,
        None,
        "The default monster ID for the partner (0x1: Bulbasaur)\n\ntype: struct"
        " monster_id_16",
    )

    GAME_MODE = Symbol(None, None, None, "[Runtime]\n\ntype: uint8_t")

    ADVENTURE_LOG_PTR = Symbol(
        [0xB17EC], [0x20B17EC], 0x4, "[Runtime]\n\ntype: struct adventure_log*"
    )

    ITEM_TABLES_PTRS_1 = Symbol(None, None, None, "")

    SMD_EVENTS_FUN_TABLE = Symbol(None, None, None, "")


class JpArm9Section:
    name = "arm9"
    description = (
        "Hard-coded immediate values (literals) in instructions within the ARM 9"
        " binary."
    )
    loadaddress = 0x2000000
    length = 0xB8CB8
    functions = JpArm9Functions
    data = JpArm9Data


class JpOverlay0Functions:
    pass


class JpOverlay0Data:
    TOP_MENU_MUSIC_ID = Symbol(None, None, None, "Music ID to play in the top menu.")


class JpOverlay0Section:
    name = "overlay0"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 0."
    )
    loadaddress = 0x22BE220
    length = 0x609A0
    functions = JpOverlay0Functions
    data = JpOverlay0Data


class JpOverlay10Functions:
    SprintfStatic = Symbol(
        None,
        None,
        None,
        "Statically defined copy of sprintf(3) in overlay 10. See arm9.yml for more"
        " information.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )


class JpOverlay10Data:
    FIRST_DUNGEON_WITH_MONSTER_HOUSE_TRAPS = Symbol(
        None,
        None,
        None,
        "The first dungeon that can have extra traps spawn in Monster Houses, Dark"
        " Hill\n\ntype: struct dungeon_id_8",
    )

    BAD_POISON_DAMAGE_COOLDOWN = Symbol(
        None,
        None,
        None,
        "The number of turns between passive bad poison (toxic) damage.",
    )

    PROTEIN_STAT_BOOST = Symbol(
        None, None, None, "The permanent attack boost from ingesting a Protein."
    )

    SPAWN_CAP_NO_MONSTER_HOUSE = Symbol(
        None,
        None,
        None,
        "The maximum number of enemies that can spawn on a floor without a monster"
        " house (15).",
    )

    OREN_BERRY_DAMAGE = Symbol(
        None, None, None, "Damage dealt by eating an Oren Berry."
    )

    SITRUS_BERRY_HP_RESTORATION = Symbol(
        None, None, None, "The amount of HP restored by eating a Sitrus Berry."
    )

    EXP_ELITE_EXP_BOOST = Symbol(
        None,
        None,
        None,
        "The percentage increase in experience from the Exp. Elite IQ skill",
    )

    MONSTER_HOUSE_MAX_NON_MONSTER_SPAWNS = Symbol(
        None,
        None,
        None,
        "The maximum number of extra non-monster spawns (items/traps) in a Monster"
        " House, 7",
    )

    GOLD_THORN_POWER = Symbol(None, None, None, "Attack power for Golden Thorns.")

    SPAWN_COOLDOWN = Symbol(
        None,
        None,
        None,
        "The number of turns between enemy spawns under normal conditions.",
    )

    ORAN_BERRY_FULL_HP_BOOST = Symbol(
        None,
        None,
        None,
        "The permanent HP boost from eating an Oran Berry at full HP (0).",
    )

    LIFE_SEED_HP_BOOST = Symbol(
        None, None, None, "The permanent HP boost from eating a Life Seed."
    )

    EXCLUSIVE_ITEM_EXP_BOOST = Symbol(
        None,
        None,
        None,
        "The percentage increase in experience from exp-boosting exclusive items",
    )

    INTIMIDATOR_ACTIVATION_CHANCE = Symbol(
        None, None, None, "The percentage chance that Intimidator will activate."
    )

    ORAN_BERRY_HP_RESTORATION = Symbol(
        None, None, None, "The amount of HP restored by eating a Oran Berry."
    )

    SITRUS_BERRY_FULL_HP_BOOST = Symbol(
        None,
        None,
        None,
        "The permanent HP boost from eating a Sitrus Berry at full HP.",
    )

    BURN_DAMAGE_COOLDOWN = Symbol(
        None, None, None, "The number of turns between passive burn damage."
    )

    STICK_POWER = Symbol(None, None, None, "Attack power for Sticks.")

    SPAWN_COOLDOWN_THIEF_ALERT = Symbol(
        None,
        None,
        None,
        "The number of turns between enemy spawns when the Thief Alert condition is"
        " active.",
    )

    MONSTER_HOUSE_MAX_MONSTER_SPAWNS = Symbol(
        None,
        None,
        None,
        "The maximum number of monster spawns in a Monster House, 30, but multiplied by"
        " 2/3 for some reason (so the actual maximum is 45)",
    )

    SPEED_BOOST_TURNS = Symbol(
        None,
        None,
        None,
        "Number of turns (250) after which Speed Boost will trigger and increase speed"
        " by one stage.",
    )

    MIRACLE_CHEST_EXP_BOOST = Symbol(
        None,
        None,
        None,
        "The percentage increase in experience from the Miracle Chest item",
    )

    WONDER_CHEST_EXP_BOOST = Symbol(
        None,
        None,
        None,
        "The percentage increase in experience from the Wonder Chest item",
    )

    SPAWN_CAP_WITH_MONSTER_HOUSE = Symbol(
        None,
        None,
        None,
        "The maximum number of enemies that can spawn on a floor with a monster house,"
        " not counting those in the monster house (4).",
    )

    POISON_DAMAGE_COOLDOWN = Symbol(
        None, None, None, "The number of turns between passive poison damage."
    )

    GEO_PEBBLE_DAMAGE = Symbol(None, None, None, "Damage dealt by Geo Pebbles.")

    GRAVELEROCK_DAMAGE = Symbol(None, None, None, "Damage dealt by Gravelerocks.")

    RARE_FOSSIL_DAMAGE = Symbol(None, None, None, "Damage dealt by Rare Fossils.")

    GINSENG_CHANCE_3 = Symbol(
        None,
        None,
        None,
        "The percentage chance for...something to be set to 3 in a calculation related"
        " to the Ginseng boost.",
    )

    ZINC_STAT_BOOST = Symbol(
        None, None, None, "The permanent special defense boost from ingesting a Zinc."
    )

    IRON_STAT_BOOST = Symbol(
        None, None, None, "The permanent defense boost from ingesting an Iron."
    )

    CALCIUM_STAT_BOOST = Symbol(
        None, None, None, "The permanent special attack boost from ingesting a Calcium."
    )

    CORSOLA_TWIG_POWER = Symbol(None, None, None, "Attack power for Corsola Twigs.")

    CACNEA_SPIKE_POWER = Symbol(None, None, None, "Attack power for Cacnea Spikes.")

    GOLD_FANG_POWER = Symbol(None, None, None, "Attack power for Gold Fangs.")

    SILVER_SPIKE_POWER = Symbol(None, None, None, "Attack power for Silver Spikes.")

    IRON_THORN_POWER = Symbol(None, None, None, "Attack power for Iron Thorns.")

    SLEEP_DURATION_RANGE = Symbol(
        None,
        None,
        None,
        "Appears to control the range of turns for which the sleep condition can"
        " last.\n\nThe first two bytes are the low value of the range, and the later"
        " two bytes are the high value.",
    )

    POWER_PITCHER_DAMAGE_MULTIPLIER = Symbol(
        None,
        None,
        None,
        "The multiplier for projectile damage from Power Pitcher (1.5), as a binary"
        " fixed-point number (8 fraction bits)",
    )

    AIR_BLADE_DAMAGE_MULTIPLIER = Symbol(
        None,
        None,
        None,
        "The multiplier for damage from the Air Blade (1.5), as a binary fixed-point"
        " number (8 fraction bits)",
    )

    SPEED_BOOST_DURATION_RANGE = Symbol(
        None,
        None,
        None,
        "Appears to control the range of turns for which a speed boost can last.\n\nThe"
        " first two bytes are the low value of the range, and the later two bytes are"
        " the high value.",
    )

    OFFENSIVE_STAT_STAGE_MULTIPLIERS = Symbol(
        None,
        None,
        None,
        "Table of multipliers for offensive stats (attack/special attack) for each"
        " stage 0-20, as binary fixed-point numbers (8 fraction bits)",
    )

    DEFENSIVE_STAT_STAGE_MULTIPLIERS = Symbol(
        None,
        None,
        None,
        "Table of multipliers for defensive stats (defense/special defense) for each"
        " stage 0-20, as binary fixed-point numbers (8 fraction bits)",
    )

    RANDOM_MUSIC_ID_TABLE = Symbol(
        None,
        None,
        None,
        "Table of music IDs for dungeons with a random assortment of music"
        " tracks.\n\nThis is a table with 30 rows, each with 4 2-byte music IDs. Each"
        " row contains the possible music IDs for a given group, from which the music"
        " track will be selected randomly.\n\ntype: struct music_id_16[30][4]",
    )

    MALE_ACCURACY_STAGE_MULTIPLIERS = Symbol(
        None,
        None,
        None,
        "Table of multipliers for the accuracy stat for males for each stage 0-20, as"
        " binary fixed-point numbers (8 fraction bits)",
    )

    MALE_EVASION_STAGE_MULTIPLIERS = Symbol(
        None,
        None,
        None,
        "Table of multipliers for the evasion stat for males for each stage 0-20, as"
        " binary fixed-point numbers (8 fraction bits)",
    )

    FEMALE_ACCURACY_STAGE_MULTIPLIERS = Symbol(
        None,
        None,
        None,
        "Table of multipliers for the accuracy stat for females for each stage 0-20, as"
        " binary fixed-point numbers (8 fraction bits)",
    )

    FEMALE_EVASION_STAGE_MULTIPLIERS = Symbol(
        None,
        None,
        None,
        "Table of multipliers for the evasion stat for females for each stage 0-20, as"
        " binary fixed-point numbers (8 fraction bits)",
    )

    MUSIC_ID_TABLE = Symbol(
        None,
        None,
        None,
        "List of music IDs used in dungeons with a single music track.\n\nThis is an"
        " array of 170 2-byte music IDs, and is indexed into by the music value in the"
        " floor properties struct for a given floor. Music IDs with the highest bit set"
        " (0x8000) are indexes into the RANDOM_MUSIC_ID_TABLE.\n\ntype: struct"
        " music_id_16[170] (or not a music ID if the highest bit is set)",
    )

    TYPE_MATCHUP_TABLE = Symbol(
        None,
        None,
        None,
        "Table of type matchups.\n\nEach row corresponds to the type matchups of a"
        " specific attack type, with each entry within the row specifying the type's"
        " effectiveness against a target type.\n\ntype: struct type_matchup_table",
    )

    FIXED_ROOM_MONSTER_SPAWN_STATS_TABLE = Symbol(
        None,
        None,
        None,
        "Table of stats for monsters that can spawn in fixed rooms, pointed into by the"
        " FIXED_ROOM_MONSTER_SPAWN_TABLE.\n\nThis is an array of 99 12-byte entries"
        " containing stat spreads for one monster entry each.\n\ntype: struct"
        " fixed_room_monster_spawn_stats_entry[99]",
    )

    TILESET_PROPERTIES = Symbol(None, None, None, "")

    FIXED_ROOM_PROPERTIES_TABLE = Symbol(
        None,
        None,
        None,
        "Table of properties for fixed rooms.\n\nThis is an array of 256 12-byte"
        " entries containing properties for a given fixed room ID.\n\nSee the struct"
        " definitions and End45's dungeon data document for more info.\n\ntype: struct"
        " fixed_room_properties_entry[256]",
    )

    MOVE_ANIMATION_INFO = Symbol(None, None, None, "")


class JpOverlay10Section:
    name = "overlay10"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 10."
    )
    loadaddress = 0x22BE220
    length = 0x1F6A0
    functions = JpOverlay10Functions
    data = JpOverlay10Data


class JpOverlay34Functions:
    pass


class JpOverlay34Data:
    UNKNOWN_MENU_CONFIRM = Symbol(None, None, None, "")

    DUNGEON_DEBUG_MENU = Symbol(None, None, None, "")


class JpOverlay34Section:
    name = "overlay34"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 34."
    )
    loadaddress = 0x22DD8E0
    length = 0xDC0
    functions = JpOverlay34Functions
    data = JpOverlay34Data


class JpOverlay1Functions:
    pass


class JpOverlay1Data:
    CONTINUE_CHOICE = Symbol(None, None, None, "")

    SUBMENU = Symbol(None, None, None, "")

    MAIN_MENU = Symbol(None, None, None, "")

    MAIN_MENU_CONFIRM = Symbol(None, None, None, "")

    MAIN_DEBUG_MENU_1 = Symbol(None, None, None, "")

    MAIN_DEBUG_MENU_2 = Symbol(None, None, None, "")


class JpOverlay1Section:
    name = "overlay1"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 1."
    )
    loadaddress = 0x232ACC0
    length = 0x12E00
    functions = JpOverlay1Functions
    data = JpOverlay1Data


class JpOverlay4Functions:
    pass


class JpOverlay4Data:
    pass


class JpOverlay4Section:
    name = "overlay4"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 4."
    )
    loadaddress = 0x233E300
    length = 0x2BE0
    functions = JpOverlay4Functions
    data = JpOverlay4Data


class JpOverlay6Functions:
    pass


class JpOverlay6Data:
    pass


class JpOverlay6Section:
    name = "overlay6"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 6."
    )
    loadaddress = 0x233E300
    length = 0x2460
    functions = JpOverlay6Functions
    data = JpOverlay6Data


class JpOverlay7Functions:
    pass


class JpOverlay7Data:
    pass


class JpOverlay7Section:
    name = "overlay7"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 7."
    )
    loadaddress = 0x233E300
    length = 0x53E0
    functions = JpOverlay7Functions
    data = JpOverlay7Data


class JpOverlay9Functions:
    pass


class JpOverlay9Data:
    TOP_MENU_RETURN_MUSIC_ID = Symbol(
        None,
        None,
        None,
        "Song playing in the main menu when returning from the Sky Jukebox.",
    )


class JpOverlay9Section:
    name = "overlay9"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 9."
    )
    loadaddress = 0x233E300
    length = 0x2D20
    functions = JpOverlay9Functions
    data = JpOverlay9Data


class JpOverlay30Functions:
    pass


class JpOverlay30Data:
    pass


class JpOverlay30Section:
    name = "overlay30"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 30."
    )
    loadaddress = 0x2383AA0
    length = 0x3880
    functions = JpOverlay30Functions
    data = JpOverlay30Data


class JpOverlay31Functions:
    pass


class JpOverlay31Data:
    DUNGEON_MAIN_MENU = Symbol(None, None, None, "")

    DUNGEON_SUBMENU_1 = Symbol(None, None, None, "")

    DUNGEON_SUBMENU_2 = Symbol(None, None, None, "")

    DUNGEON_SUBMENU_3 = Symbol(None, None, None, "")

    DUNGEON_SUBMENU_4 = Symbol(None, None, None, "")

    DUNGEON_SUBMENU_5 = Symbol(None, None, None, "")

    DUNGEON_SUBMENU_6 = Symbol(None, None, None, "")


class JpOverlay31Section:
    name = "overlay31"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 31."
    )
    loadaddress = 0x2383AA0
    length = 0x7AC0
    functions = JpOverlay31Functions
    data = JpOverlay31Data


class JpOverlay13Functions:
    pass


class JpOverlay13Data:
    STARTERS_PARTNER_IDS = Symbol(None, None, None, "type: struct monster_id_16[21]")

    STARTERS_HERO_IDS = Symbol(None, None, None, "type: struct monster_id_16[32]")

    STARTERS_STRINGS = Symbol(None, None, None, "")

    QUIZ_QUESTION_STRINGS = Symbol(None, None, None, "")

    QUIZ_ANSWER_STRINGS = Symbol(None, None, None, "")

    UNKNOWN_MENU_1 = Symbol(None, None, None, "")


class JpOverlay13Section:
    name = "overlay13"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 13."
    )
    loadaddress = 0x238B6A0
    length = 0x2E80
    functions = JpOverlay13Functions
    data = JpOverlay13Data


class JpOverlay14Functions:
    pass


class JpOverlay14Data:
    FOOTPRINT_DEBUG_MENU = Symbol(None, None, None, "")


class JpOverlay14Section:
    name = "overlay14"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 14."
    )
    loadaddress = 0x238B6A0
    length = 0x3AE0
    functions = JpOverlay14Functions
    data = JpOverlay14Data


class JpOverlay15Functions:
    pass


class JpOverlay15Data:
    BANK_MAIN_MENU = Symbol(None, None, None, "")


class JpOverlay15Section:
    name = "overlay15"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 15."
    )
    loadaddress = 0x238B6A0
    length = 0x1060
    functions = JpOverlay15Functions
    data = JpOverlay15Data


class JpOverlay16Functions:
    pass


class JpOverlay16Data:
    EVO_MENU_CONFIRM = Symbol(None, None, None, "")

    EVO_SUBMENU = Symbol(None, None, None, "")

    EVO_MAIN_MENU = Symbol(None, None, None, "")


class JpOverlay16Section:
    name = "overlay16"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 16."
    )
    loadaddress = 0x238B6A0
    length = 0x2D40
    functions = JpOverlay16Functions
    data = JpOverlay16Data


class JpOverlay18Functions:
    pass


class JpOverlay18Data:
    MOVES_MENU_CONFIRM = Symbol(None, None, None, "")

    MOVES_SUBMENU_1 = Symbol(None, None, None, "")

    MOVES_SUBMENU_2 = Symbol(None, None, None, "")

    MOVES_MAIN_MENU = Symbol(None, None, None, "")

    MOVES_SUBMENU_3 = Symbol(None, None, None, "")

    MOVES_SUBMENU_4 = Symbol(None, None, None, "")

    MOVES_SUBMENU_5 = Symbol(None, None, None, "")

    MOVES_SUBMENU_6 = Symbol(None, None, None, "")

    MOVES_SUBMENU_7 = Symbol(None, None, None, "")


class JpOverlay18Section:
    name = "overlay18"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 18."
    )
    loadaddress = 0x238B6A0
    length = 0x3520
    functions = JpOverlay18Functions
    data = JpOverlay18Data


class JpOverlay21Functions:
    pass


class JpOverlay21Data:
    SWAP_SHOP_MENU_CONFIRM = Symbol(None, None, None, "")

    SWAP_SHOP_SUBMENU_1 = Symbol(None, None, None, "")

    SWAP_SHOP_SUBMENU_2 = Symbol(None, None, None, "")

    SWAP_SHOP_MAIN_MENU_1 = Symbol(None, None, None, "")

    SWAP_SHOP_MAIN_MENU_2 = Symbol(None, None, None, "")

    SWAP_SHOP_SUBMENU_3 = Symbol(None, None, None, "")


class JpOverlay21Section:
    name = "overlay21"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 21."
    )
    loadaddress = 0x238B6A0
    length = 0x2E40
    functions = JpOverlay21Functions
    data = JpOverlay21Data


class JpOverlay22Functions:
    pass


class JpOverlay22Data:
    SHOP_MENU_CONFIRM = Symbol(None, None, None, "")

    SHOP_MAIN_MENU_1 = Symbol(None, None, None, "")

    SHOP_MAIN_MENU_2 = Symbol(None, None, None, "")

    SHOP_MAIN_MENU_3 = Symbol(None, None, None, "")


class JpOverlay22Section:
    name = "overlay22"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 22."
    )
    loadaddress = 0x238B6A0
    length = 0x4B40
    functions = JpOverlay22Functions
    data = JpOverlay22Data


class JpOverlay23Functions:
    pass


class JpOverlay23Data:
    STORAGE_MENU_CONFIRM = Symbol(None, None, None, "")

    STORAGE_MAIN_MENU_1 = Symbol(None, None, None, "")

    STORAGE_MAIN_MENU_2 = Symbol(None, None, None, "")

    STORAGE_MAIN_MENU_3 = Symbol(None, None, None, "")

    STORAGE_MAIN_MENU_4 = Symbol(None, None, None, "")


class JpOverlay23Section:
    name = "overlay23"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 23."
    )
    loadaddress = 0x238B6A0
    length = 0x37E0
    functions = JpOverlay23Functions
    data = JpOverlay23Data


class JpOverlay24Functions:
    pass


class JpOverlay24Data:
    DAYCARE_MENU_CONFIRM = Symbol(None, None, None, "")

    DAYCARE_MAIN_MENU = Symbol(None, None, None, "")


class JpOverlay24Section:
    name = "overlay24"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 24."
    )
    loadaddress = 0x238B6A0
    length = 0x24E0
    functions = JpOverlay24Functions
    data = JpOverlay24Data


class JpOverlay26Functions:
    pass


class JpOverlay26Data:
    pass


class JpOverlay26Section:
    name = "overlay26"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 26."
    )
    loadaddress = 0x238B6A0
    length = 0xE40
    functions = JpOverlay26Functions
    data = JpOverlay26Data


class JpOverlay27Functions:
    pass


class JpOverlay27Data:
    DISCARD_ITEMS_MENU_CONFIRM = Symbol(None, None, None, "")

    DISCARD_ITEMS_SUBMENU_1 = Symbol(None, None, None, "")

    DISCARD_ITEMS_SUBMENU_2 = Symbol(None, None, None, "")

    DISCARD_ITEMS_MAIN_MENU = Symbol(None, None, None, "")


class JpOverlay27Section:
    name = "overlay27"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 27."
    )
    loadaddress = 0x238B6A0
    length = 0x2DA0
    functions = JpOverlay27Functions
    data = JpOverlay27Data


class JpOverlay32Functions:
    pass


class JpOverlay32Data:
    pass


class JpOverlay32Section:
    name = "overlay32"
    description = "Unused; all zeroes."
    loadaddress = 0x2383AA0
    length = 0x20
    functions = JpOverlay32Functions
    data = JpOverlay32Data


class JpRamFunctions:
    pass


class JpRamData:
    DUNGEON_COLORMAP_PTR = Symbol(
        None,
        None,
        None,
        "Pointer to a colormap used to render colors in a dungeon.\n\nThe colormap is a"
        " list of 4-byte RGB colors of the form {R, G, B, padding}, which the game"
        " indexes into when rendering colors. Some weather conditions modify the"
        " colormap, which is how the color scheme changes when it's, e.g., raining.",
    )

    DUNGEON_STRUCT = Symbol(
        None,
        None,
        None,
        "The dungeon context struct used for tons of stuff in dungeon mode. See struct"
        " dungeon in the C headers.\n\nThis struct never seems to be referenced"
        " directly, and is instead usually accessed via DUNGEON_PTR in overlay"
        " 29.\n\ntype: struct dungeon",
    )

    MOVE_DATA_TABLE = Symbol(
        None,
        None,
        None,
        "The move data table loaded directly from /BALANCE/waza_p.bin. See struct"
        " move_data_table in the C headers.\n\nPointed to by MOVE_DATA_TABLE_PTR in the"
        " ARM 9 binary.\n\ntype: struct move_data_table",
    )

    FRAMES_SINCE_LAUNCH = Symbol(
        None,
        None,
        None,
        "Starts at 0 when the game is first launched, and continuously ticks up once"
        " per frame while the game is running.",
    )

    BAG_ITEMS = Symbol(
        None,
        None,
        None,
        "Array of item structs within the player's bag.\n\nWhile the game only allows a"
        " maximum of 48 items during normal play, it seems to read up to 50 item slots"
        " if filled.\n\ntype: struct item[50]",
    )

    BAG_ITEMS_PTR = Symbol(None, None, None, "Pointer to BAG_ITEMS.")

    STORAGE_ITEMS = Symbol(
        None,
        None,
        None,
        "Array of item IDs in the player's item storage.\n\nFor stackable items, the"
        " quantities are stored elsewhere, in STORAGE_ITEM_QUANTITIES.\n\ntype: struct"
        " item_id_16[1000]",
    )

    STORAGE_ITEM_QUANTITIES = Symbol(
        None,
        None,
        None,
        "Array of 1000 2-byte (unsigned) quantities corresponding to the item IDs in"
        " STORAGE_ITEMS.\n\nIf the corresponding item ID is not a stackable item, the"
        " entry in this array is unused, and will be 0.",
    )

    KECLEON_SHOP_ITEMS_PTR = Symbol(None, None, None, "Pointer to KECLEON_SHOP_ITEMS.")

    KECLEON_SHOP_ITEMS = Symbol(
        None,
        None,
        None,
        "Array of up to 8 items in the Kecleon Shop of the form {struct item_id_16 id,"
        " uint16_t quantity}.\n\nIf there are fewer than 8 items, the array is expected"
        " to be null-terminated.",
    )

    UNUSED_KECLEON_SHOP_ITEMS = Symbol(
        None,
        None,
        None,
        "Seems to be another array like KECLEON_SHOP_ITEMS, but don't actually appear"
        " to be used by the Kecleon Shop.",
    )

    KECLEON_WARES_ITEMS_PTR = Symbol(
        None, None, None, "Pointer to KECLEON_WARES_ITEMS."
    )

    KECLEON_WARES_ITEMS = Symbol(
        None,
        None,
        None,
        "Array of up to 4 items in Kecleon Wares of the form {struct item_id_16 id,"
        " uint16_t quantity}.\n\nIf there are fewer than 4 items, the array is expected"
        " to be null-terminated.",
    )

    UNUSED_KECLEON_WARES_ITEMS = Symbol(
        None,
        None,
        None,
        "Seems to be another array like KECLEON_WARES_ITEMS, but don't actually appear"
        " to be used by Kecleon Wares.",
    )

    MONEY_CARRIED = Symbol(
        None, None, None, "The amount of money the player is currently carrying."
    )

    MONEY_STORED = Symbol(
        None,
        None,
        None,
        "The amount of money the player currently has stored in the Duskull Bank.",
    )

    LAST_NEW_MOVE = Symbol(
        None,
        None,
        None,
        "Move struct of the last new move introduced when learning a new move. Persists"
        " even after the move selection is made in the menu.\n\ntype: struct move",
    )

    SCRIPT_VARS_VALUES = Symbol(
        None,
        None,
        None,
        "The table of game variable values. Its structure is determined by"
        " SCRIPT_VARS.\n\nNote that with the script variable list defined in"
        " SCRIPT_VARS, the used length of this table is actually only 0x2B4. However,"
        " the real length of this table is 0x400 based on the game code.\n\ntype:"
        " struct script_var_value_table",
    )

    BAG_LEVEL = Symbol(
        None,
        None,
        None,
        "The player's bag level, which determines the bag capacity. This indexes"
        " directly into the BAG_CAPACITY_TABLE in the ARM9 binary.",
    )

    DEBUG_SPECIAL_EPISODE_NUMBER = Symbol(
        None,
        None,
        None,
        "The number of the special episode currently being played.\n\n0: normal,"
        " Bidoof's Wish\n1: Igglybuff the Prodigy\n2: Today's 'Oh My Gosh'\n3: Here"
        " Comes Team Charm!\n4: In the Future of Darkness",
    )

    PENDING_DUNGEON_ID = Symbol(
        None,
        None,
        None,
        "The ID of the selected dungeon when setting off from the"
        " overworld.\n\nControls the text and map location during the 'map cutscene'"
        " just before entering a dungeon, as well as the actual dungeon loaded"
        " afterwards.\n\ntype: struct dungeon_id_8",
    )

    PENDING_STARTING_FLOOR = Symbol(
        None,
        None,
        None,
        "The floor number to start from in the dungeon specified by"
        " PENDING_DUNGEON_ID.",
    )

    PLAY_TIME_SECONDS = Symbol(
        None, None, None, "The player's total play time in seconds."
    )

    PLAY_TIME_FRAME_COUNTER = Symbol(
        None,
        None,
        None,
        "Counts from 0-59 in a loop, with the play time being incremented by 1 second"
        " with each rollover.",
    )

    TEAM_NAME = Symbol(
        None,
        None,
        None,
        "The team name.\n\nA null-terminated string, with a maximum length of 10."
        " Presumably encoded with the ANSI/Shift JIS encoding the game typically"
        " uses.\n\nThis is presumably part of a larger struct, together with other"
        " nearby data.",
    )

    HERO_SPECIES_ID = Symbol(
        None,
        None,
        None,
        "The hero's species ID.\n\nThis is presumably part of a larger struct, together"
        " with other nearby data.\n\ntype: struct monster_id_16",
    )

    HERO_NICKNAME = Symbol(
        None,
        None,
        None,
        "The hero's nickname.\n\nA null-terminated string, with a maximum length of 10."
        " Presumably encoded with the ANSI/Shift JIS encoding the game typically"
        " uses.\n\nThis is presumably part of a larger struct, together with other"
        " nearby data.",
    )

    PARTNER_SPECIES_ID = Symbol(
        None,
        None,
        None,
        "The partner's species ID.\n\nThis is presumably part of a larger struct,"
        " together with other nearby data.\n\ntype: struct monster_id_16",
    )

    LEADER_IQ_SKILLS = Symbol(
        None,
        None,
        None,
        "Unlocked IQ skills of the current leader, available for selection from the IQ"
        " skills menu.\n\nOne bit per skill (1 if unlocked). Same format as the IQ"
        " skills bitvector on the monster info struct.\n\nThis is presumably part of a"
        " larger struct, together with other nearby data.",
    )

    LEADER_NICKNAME = Symbol(
        None,
        None,
        None,
        "The current leader's nickname.\n\nA null-terminated string, with a maximum"
        " length of 10. Presumably encoded with the ANSI/Shift JIS encoding the game"
        " typically uses.\n\nThis is presumably part of a larger struct, together with"
        " other nearby data.",
    )

    PARTY_MEMBER_2_IQ_SKILLS = Symbol(
        None,
        None,
        None,
        "Unlocked IQ skills of the second party member, available for selection from"
        " the IQ skills menu.\n\nOne bit per skill (1 if unlocked). Same format as the"
        " IQ skills bitvector on the monster info struct.\n\nThis is presumably part of"
        " a larger struct, together with other nearby data.",
    )

    FRAMES_SINCE_LAUNCH_TIMES_THREE = Symbol(
        None,
        None,
        None,
        "Starts at 0 when the game is first launched, and ticks up by 3 per frame while"
        " the game is running.",
    )

    TURNING_ON_THE_SPOT_FLAG = Symbol(
        None,
        None,
        None,
        "[Runtime] Flag for whether the player is turning on the spot (pressing Y).",
    )

    FLOOR_GENERATION_STATUS = Symbol(
        None,
        None,
        None,
        "[Runtime] Status data related to generation of the current floor in a"
        " dungeon.\n\nThis data is populated as the dungeon floor is"
        " generated.\n\ntype: struct floor_generation_status",
    )


class JpRamSection:
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
    functions = JpRamFunctions
    data = JpRamData


class JpOverlay35Functions:
    pass


class JpOverlay35Data:
    pass


class JpOverlay35Section:
    name = "overlay35"
    description = "Unused; all zeroes."
    loadaddress = 0x22BE220
    length = 0x20
    functions = JpOverlay35Functions
    data = JpOverlay35Data


class JpOverlay33Functions:
    pass


class JpOverlay33Data:
    pass


class JpOverlay33Section:
    name = "overlay33"
    description = "Unused; all zeroes."
    loadaddress = 0x2383AA0
    length = 0x20
    functions = JpOverlay33Functions
    data = JpOverlay33Data


class JpSections:
    overlay20 = JpOverlay20Section

    overlay3 = JpOverlay3Section

    overlay8 = JpOverlay8Section

    overlay5 = JpOverlay5Section

    overlay17 = JpOverlay17Section

    overlay19 = JpOverlay19Section

    overlay12 = JpOverlay12Section

    overlay2 = JpOverlay2Section

    overlay28 = JpOverlay28Section

    overlay29 = JpOverlay29Section

    overlay11 = JpOverlay11Section

    overlay25 = JpOverlay25Section

    arm9 = JpArm9Section

    overlay0 = JpOverlay0Section

    overlay10 = JpOverlay10Section

    overlay34 = JpOverlay34Section

    overlay1 = JpOverlay1Section

    overlay4 = JpOverlay4Section

    overlay6 = JpOverlay6Section

    overlay7 = JpOverlay7Section

    overlay9 = JpOverlay9Section

    overlay30 = JpOverlay30Section

    overlay31 = JpOverlay31Section

    overlay13 = JpOverlay13Section

    overlay14 = JpOverlay14Section

    overlay15 = JpOverlay15Section

    overlay16 = JpOverlay16Section

    overlay18 = JpOverlay18Section

    overlay21 = JpOverlay21Section

    overlay22 = JpOverlay22Section

    overlay23 = JpOverlay23Section

    overlay24 = JpOverlay24Section

    overlay26 = JpOverlay26Section

    overlay27 = JpOverlay27Section

    overlay32 = JpOverlay32Section

    ram = JpRamSection

    overlay35 = JpOverlay35Section

    overlay33 = JpOverlay33Section

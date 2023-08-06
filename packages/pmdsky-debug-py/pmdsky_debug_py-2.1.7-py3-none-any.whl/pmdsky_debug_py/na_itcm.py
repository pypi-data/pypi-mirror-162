from .protocol import Symbol


class NaItcmOverlay20Functions:
    pass


class NaItcmOverlay20Data:
    RECYCLE_MENU_CONFIRM_1 = Symbol(None, None, None, "")

    RECYCLE_MENU_CONFIRM_2 = Symbol(None, None, None, "")

    RECYCLE_SUBMENU_1 = Symbol(None, None, None, "")

    RECYCLE_SUBMENU_2 = Symbol(None, None, None, "")

    RECYCLE_MAIN_MENU_1 = Symbol(None, None, None, "")

    RECYCLE_MAIN_MENU_2 = Symbol(None, None, None, "")

    RECYCLE_MAIN_MENU_3 = Symbol(None, None, None, "")


class NaItcmOverlay20Section:
    name = "overlay20"
    description = "Controls the Recycle Shop."
    loadaddress = None
    length = None
    functions = NaItcmOverlay20Functions
    data = NaItcmOverlay20Data


class NaItcmOverlay3Functions:
    pass


class NaItcmOverlay3Data:
    pass


class NaItcmOverlay3Section:
    name = "overlay3"
    description = "Controls the Friend Rescue submenu within the top menu."
    loadaddress = None
    length = None
    functions = NaItcmOverlay3Functions
    data = NaItcmOverlay3Data


class NaItcmOverlay8Functions:
    pass


class NaItcmOverlay8Data:
    pass


class NaItcmOverlay8Section:
    name = "overlay8"
    description = (
        "Controls the Send Demo Dungeon submenu within the top menu (under 'Other')."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay8Functions
    data = NaItcmOverlay8Data


class NaItcmOverlay5Functions:
    pass


class NaItcmOverlay5Data:
    pass


class NaItcmOverlay5Section:
    name = "overlay5"
    description = "Controls the Trade Team submenu within the top menu."
    loadaddress = None
    length = None
    functions = NaItcmOverlay5Functions
    data = NaItcmOverlay5Data


class NaItcmOverlay17Functions:
    pass


class NaItcmOverlay17Data:
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


class NaItcmOverlay17Section:
    name = "overlay17"
    description = "Controls the Chimecho Assembly."
    loadaddress = None
    length = None
    functions = NaItcmOverlay17Functions
    data = NaItcmOverlay17Data


class NaItcmOverlay19Functions:
    pass


class NaItcmOverlay19Data:
    BAR_MENU_CONFIRM_1 = Symbol(None, None, None, "")

    BAR_MENU_CONFIRM_2 = Symbol(None, None, None, "")

    BAR_MAIN_MENU = Symbol(None, None, None, "")

    BAR_SUBMENU_1 = Symbol(None, None, None, "")

    BAR_SUBMENU_2 = Symbol(None, None, None, "")


class NaItcmOverlay19Section:
    name = "overlay19"
    description = "Controls Spinda's Juice Bar."
    loadaddress = None
    length = None
    functions = NaItcmOverlay19Functions
    data = NaItcmOverlay19Data


class NaItcmOverlay12Functions:
    pass


class NaItcmOverlay12Data:
    pass


class NaItcmOverlay12Section:
    name = "overlay12"
    description = "Unused; all zeroes."
    loadaddress = None
    length = None
    functions = NaItcmOverlay12Functions
    data = NaItcmOverlay12Data


class NaItcmOverlay2Functions:
    pass


class NaItcmOverlay2Data:
    pass


class NaItcmOverlay2Section:
    name = "overlay2"
    description = (
        "Controls the Nintendo WFC Settings interface, accessed from the top menu"
        " (Other > Nintendo WFC > Nintendo WFC Settings). Presumably contains code for"
        " Nintendo Wi-Fi setup."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay2Functions
    data = NaItcmOverlay2Data


class NaItcmOverlay28Functions:
    pass


class NaItcmOverlay28Data:
    pass


class NaItcmOverlay28Section:
    name = "overlay28"
    description = "Controls the staff credits sequence."
    loadaddress = None
    length = None
    functions = NaItcmOverlay28Functions
    data = NaItcmOverlay28Data


class NaItcmOverlay29Functions:
    DungeonAlloc = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Get the current floor type.\n\nFloor types:\n  0 appears to mean the current"
        " floor is 'normal'\n  1 appears to mean the current floor is a fixed floor\n "
        " 2 means the current floor has a rescue point\n\nreturn: floor type",
    )

    TryForcedLoss = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Get the id of the monster to be randomly spawned.\n\nr0: the spawn weight to"
        " use (0 for normal, 1 for monster house)\nreturn: monster ID",
    )

    GetMonsterLevelToSpawn = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Gets the current preseed stored in the global dungeon PRNG state. See"
        " GenerateDungeonRngSeed for more information.\n\nreturn: current dungeon RNG"
        " preseed",
    )

    SetDungeonRngPreseed = Symbol(
        None,
        None,
        None,
        "Sets the preseed in the global dungeon PRNG state. See GenerateDungeonRngSeed"
        " for more information.\n\nr0: preseed",
    )

    InitDungeonRng = Symbol(
        None,
        None,
        None,
        "Initialize (or reinitialize) the dungeon PRNG with a given seed. The primary"
        " LCG and the five secondary LCGs are initialized jointly, and with the same"
        " seed.\n\nr0: seed",
    )

    DungeonRand16Bit = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Compute a pseudorandom integer under a given maximum value using the dungeon"
        " PRNG.\n\nr0: high\nreturn: pseudorandom integer on the interval [0, high"
        " - 1]",
    )

    DungeonRandRange = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Seems to calculate the duration of a volatile status on a monster.\n\nr0:"
        " entity pointer\nr1: pointer to a turn range (an array of two shorts {lower,"
        " higher})\nr2: flag for whether or not to factor in the Self Curer IQ skill"
        " and the Natural Cure ability\nreturn: number of turns for the status"
        " condition",
    )

    DungeonRngUnsetSecondary = Symbol(
        None,
        None,
        None,
        "Sets the dungeon PRNG to use the primary LCG for subsequent random number"
        " generation, and also resets the secondary LCG index back to 0.\n\nSimilar to"
        " DungeonRngSetPrimary, but DungeonRngSetPrimary doesn't modify the secondary"
        " LCG index if it was already set to something other than 0.\n\nNo params.",
    )

    DungeonRngSetSecondary = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Called at the beginning of RunFractionalTurn. Executed only if"
        " FRACTIONAL_TURN_SEQUENCE[fractional_turn * 2] is not 0.\n\nFirst it calls"
        " TrySpawnMonsterAndTickSpawnCounter, then tries to activate the Plus and Minus"
        " abilities for both allies and enemies, and finally calls TryForcedLoss.\n\nNo"
        " params.",
    )

    IsFloorOver = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Checks if the current dungeon floor number is even.\n\nHas a special check to"
        " return false for Labyrinth Cave B10F (the Gabite boss fight).\n\nreturn:"
        " bool",
    )

    GetKecleonIdToSpawnByFloor = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Runs a check over all monsters on the field for the ability Slow Start, and"
        " lowers the speed of those who have it.\n\nNo params",
    )

    TryActivateArtificialWeatherAbilities = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Returns an entity pointer to the first team member which has the specified iq"
        " skill.\n\nr0: iq skill id\nreturn: pointer to entity",
    )

    TeamMemberHasEnabledIqSkill = Symbol(
        None,
        None,
        None,
        "Returns true if any team member has the specified iq skill.\n\nr0: iq skill"
        " id\nreturn: bool",
    )

    TeamLeaderIqSkillIsEnabled = Symbol(
        None,
        None,
        None,
        "Returns true the leader has the specified iq skill.\n\nr0: iq skill"
        " id\nreturn: bool",
    )

    HasLowHealth = Symbol(
        None,
        None,
        None,
        "Checks if the entity passed is a valid monster, and if it's at low health"
        " (below 25% rounded down)\n\nr0: entity pointer\nreturn: bool",
    )

    IsSpecialStoryAlly = Symbol(
        None,
        None,
        None,
        "Checks if a monster is a special story ally.\n\nThis is a hard-coded check"
        " that looks at the monster's 'Joined At' field. If the value is in the range"
        " [DUNGEON_JOINED_AT_BIDOOF, DUNGEON_DUMMY_0xE3], this check will return"
        " true.\n\nr0: monster pointer\nreturn: bool",
    )

    IsExperienceLocked = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Returns the number of attacks that a monster can do in one turn (1 or"
        " 2).\n\nChecks for the abilities Swift Swim, Chlorophyll, Unburden, and for"
        " exclusive items.\n\nr0: pointer to entity\nreturns: int",
    )

    SprintfStatic = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Checks if a monster does not have the Gastro Acid status.\n\nr0: entity"
        " pointer\nreturn: bool",
    )

    AbilityIsActive = Symbol(
        None,
        None,
        None,
        "Checks if a monster has a certain ability that isn't disabled by Gastro"
        " Acid.\n\nr0: entity pointer\nr1: ability ID\nreturn: bool",
    )

    LevitateIsActive = Symbol(
        None,
        None,
        None,
        "Checks if a monster is levitating (has the effect of Levitate and Gravity is"
        " not active).\n\nr0: pointer to entity\nreturn: bool",
    )

    MonsterIsType = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Gets the power of a move, factoring in Ginseng/Space Globe boosts.\n\nr0: user"
        " pointer\nr1: move pointer\nreturn: move power",
    )

    AddExpSpecial = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Cures the target's freeze, shadow hold, ingrain, petrified, constriction or"
        " wrap (both as user and as target) status due to the action of the"
        " user.\n\nr0: pointer to user\nr1: pointer to target\nr2: if true, the event"
        " will be printed to the log",
    )

    EndCringeClassStatus = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Appears to calculate damage from a fixed-damage effect.\n\nr0: attacker"
        " pointer\nr1: defender pointer\nr2: fixed damage\nr3: ?\nstack[0]: [output]"
        " struct containing info about the damage calculation\nstack[1]: attack"
        " type\nstack[2]: move category\nstack[3]: ?\nstack[4]: message"
        " type\nothers: ?",
    )

    CalcDamageFixedNoCategory = Symbol(
        None,
        None,
        None,
        "A wrapper around CalcDamageFixed with the move category set to none.\n\nr0:"
        " attacker pointer\nr1: defender pointer\nr2: fixed damage\nstack[0]: [output]"
        " struct containing info about the damage calculation\nstack[1]: attack"
        " type\nothers: ?",
    )

    CalcDamageFixedWrapper = Symbol(
        None,
        None,
        None,
        "A wrapper around CalcDamageFixed.\n\nr0: attacker pointer\nr1: defender"
        " pointer\nr2: fixed damage\nstack[0]: [output] struct containing info about"
        " the damage calculation\nstack[1]: attack type\nstack[2]: move"
        " category\nothers: ?",
    )

    ResetDamageCalcScratchSpace = Symbol(
        None,
        None,
        None,
        "CalcDamage seems to use scratch space of some kind, which this function"
        " zeroes.\n\nNo params.",
    )

    TrySpawnMonsterAndTickSpawnCounter = Symbol(
        None,
        None,
        None,
        "First ticks up the spawn counter, and if it's equal or greater than the spawn"
        " cooldown, it will try to spawn an enemy if the number of enemies is below the"
        " spawn cap.\n\nIf the spawn counter is greater than 900, it will instead"
        " perform the special spawn caused by the ability Illuminate.\n\nNo params.",
    )

    AuraBowIsActive = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Checks if the entity is a team member and holds the No-Slip Cap, and if so"
        " attempts to make one item in the bag sticky.\n\nr0: pointer to entity",
    )

    TickStatusAndHealthRegen = Symbol(
        None,
        None,
        None,
        "Applies the natural HP regen effect by taking modifiers into account (Poison"
        " Heal, Heal Ribbon, weather-related regen). Then it ticks down counters for"
        " volatile status effects, and heals them if the counter reached zero.\n\nr0:"
        " pointer to entity",
    )

    InflictSleepStatusSingle = Symbol(
        None,
        None,
        None,
        "This is called by TryInflictSleepStatus.\n\nr0: entity pointer\nr1: number of"
        " turns",
    )

    TryInflictSleepStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Sleep status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: number of turns\nr3: flag"
        " to log a message on failure",
    )

    TryInflictNightmareStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Nightmare status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: number"
        " of turns",
    )

    TryInflictNappingStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Napping status condition (from Rest) on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: number"
        " of turns",
    )

    TryInflictYawningStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Yawning status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: number of turns",
    )

    TryInflictSleeplessStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Sleepless status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    TryInflictPausedStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Paused status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: ?\nr3: number of"
        " turns\nstack[0]: flag to log a message on failure\nstack[1]: flag to only"
        " perform the check for inflicting without actually inflicting\nreturn: Whether"
        " or not the status could be inflicted",
    )

    TryInflictInfatuatedStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Infatuated status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    TryInflictBurnStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Burn status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to apply some"
        " special effect alongside the burn?\nr3: flag to log a message on"
        " failure\nstack[0]: flag to only perform the check for inflicting without"
        " actually inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictBurnStatusWholeTeam = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Inflicts the Frozen status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure",
    )

    TryInflictConstrictionStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Constriction status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2:"
        " animation ID\nr3: flag to log a message on failure",
    )

    TryInflictShadowHoldStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Shadow Hold (AKA Immobilized) status condition on a target"
        " monster if possible.\n\nr0: user entity pointer\nr1: target entity"
        " pointer\nr2: flag to log a message on failure",
    )

    TryInflictIngrainStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Ingrain status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer",
    )

    TryInflictWrappedStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Wrapped status condition on a target monster if possible.\n\nThis"
        " also gives the user the Wrap status (Wrapped around foe).\n\nr0: user entity"
        " pointer\nr1: target entity pointer",
    )

    FreeOtherWrappedMonsters = Symbol(
        None,
        None,
        None,
        "Frees from the wrap status all monsters which are wrapped by/around the"
        " monster passed as parameter.\n\nr0: pointer to entity",
    )

    TryInflictPetrifiedStatus = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Lowers the specified defensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of"
        " stages\nstack[0]: ?\nstack[1]: ?",
    )

    BoostOffensiveStat = Symbol(
        None,
        None,
        None,
        "Boosts the specified offensive stat on the target monster.\n\nr0: user entity"
        " pointer\nr1: target entity pointer\nr2: stat index\nr3: number of stages",
    )

    BoostDefensiveStat = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Applies a multiplier to the specified defensive stat on the target"
        " monster.\n\nThis affects struct"
        " monster_stat_modifiers::defensive_multipliers, for moves like Screech.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: stat index\nr3:"
        " multiplier\nstack[0]: ?",
    )

    BoostHitChanceStat = Symbol(
        None,
        None,
        None,
        "Boosts the specified hit chance stat (accuracy or evasion) on the target"
        " monster.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: stat"
        " index",
    )

    LowerHitChanceStat = Symbol(
        None,
        None,
        None,
        "Lowers the specified hit chance stat (accuracy or evasion) on the target"
        " monster.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: stat"
        " index\nr3: ?",
    )

    TryInflictCringeStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Cringe status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictParalysisStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Paralysis status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    BoostSpeed = Symbol(
        None,
        None,
        None,
        "Boosts the speed of the target monster.\n\nIf the number of turns specified is"
        " 0, a random turn count will be selected using the default"
        " SPEED_BOOST_DURATION_RANGE.\n\nr0: user entity pointer\nr1: target entity"
        " pointer\nr2: number of stages\nr3: number of turns\nstack[0]: flag to log a"
        " message on failure",
    )

    BoostSpeedOneStage = Symbol(
        None,
        None,
        None,
        "A wrapper around BoostSpeed with the number of stages set to 1.\n\nr0: user"
        " entity pointer\nr1: target entity pointer\nr2: number of turns\nr3: flag to"
        " log a message on failure",
    )

    LowerSpeed = Symbol(
        None,
        None,
        None,
        "Lowers the speed of the target monster.\n\nr0: user entity pointer\nr1: target"
        " entity pointer\nr2: number of stages\nr3: flag to log a message on failure",
    )

    TrySealMove = Symbol(
        None,
        None,
        None,
        "Seals one of the target monster's moves. The move to be sealed is randomly"
        " selected.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nreturn: Whether or not a move was sealed",
    )

    BoostOrLowerSpeed = Symbol(
        None,
        None,
        None,
        "Randomly boosts or lowers the speed of the target monster by one stage with"
        " equal probability.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    ResetHitChanceStat = Symbol(
        None,
        None,
        None,
        "Resets the specified hit chance stat (accuracy or evasion) back to normal on"
        " the target monster.\n\nr0: user entity pointer\nr1: target entity"
        " pointer\nr2: stat index\nr3: ?",
    )

    TryActivateQuickFeet = Symbol(
        None,
        None,
        None,
        "Activate the Quick Feet ability on the defender, if the monster has it and"
        " it's active.\n\nr0: attacker pointer\nr1: defender pointer\nreturn: bool,"
        " whether or not the ability was activated",
    )

    TryInflictConfusedStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Confused status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryInflictCoweringStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Cowering status condition on a target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: flag to log a message on"
        " failure\nr3: flag to only perform the check for inflicting without actually"
        " inflicting\nreturn: Whether or not the status could be inflicted",
    )

    TryIncreaseHp = Symbol(
        None,
        None,
        None,
        "Restore HP and possibly boost max HP of the target monster if possible.\n\nr0:"
        " user entity pointer\nr1: target entity pointer\nr2: HP to restore\nr3: max HP"
        " boost\nstack[0]: flag to log a message on failure\nreturn: Success flag",
    )

    TryInflictLeechSeedStatus = Symbol(
        None,
        None,
        None,
        "Inflicts the Leech Seed status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: flag to"
        " log a message on failure\nr3: flag to only perform the check for inflicting"
        " without actually inflicting\nreturn: Whether or not the status could be"
        " inflicted",
    )

    TryInflictDestinyBond = Symbol(
        None,
        None,
        None,
        "Inflicts the Destiny Bond status condition on a target monster if"
        " possible.\n\nr0: user entity pointer\nr1: target entity pointer",
    )

    IsBlinded = Symbol(
        None,
        None,
        None,
        "Returns true if the monster has the blinded status (see statuses::blinded), or"
        " if it is not the leader and is holding Y-Ray Specs.\n\nr0: pointer to"
        " entity\nr1: flag for whether to check for the held item\nreturn: bool",
    )

    RestoreMovePP = Symbol(
        None,
        None,
        None,
        "Restores the PP of all the target's moves by the specified amount.\n\nr0: user"
        " entity pointer\nr1: target entity pointer\nr2: PP to restore\nr3: flag to"
        " suppress message logging",
    )

    SetReflectDamageCountdownTo4 = Symbol(
        None,
        None,
        None,
        "Sets the monster's reflect damage countdown to a global value (0x4).\n\nr0:"
        " pointer to entity",
    )

    HasConditionalGroundImmunity = Symbol(
        None,
        None,
        None,
        "Checks if a monster is currently immune to Ground-type moves for reasons other"
        " than typing and ability.\n\nThis includes checks for Gravity and Magnet"
        " Rise.\n\nr0: entity pointer\nreturn: bool",
    )

    Conversion2IsActive = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Gets the move target-and-range field when used by a given entity. See struct"
        " move_target_and_range in the C headers.\n\nr0: entity pointer\nr1: move"
        " pointer\nr2: AI flag (same as GetMoveTargetAndRange)\nreturn: move target and"
        " range",
    )

    ApplyItemEffect = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Applies the IQ and possible stat boosts from eating a Gummi to the target"
        " monster.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: Gummi"
        " type ID\nr3: Stat boost amount, if a random stat boost occurs",
    )

    GetMaxPpWrapper = Symbol(
        None,
        None,
        None,
        "Gets the maximum PP for a given move. A wrapper around the function in the ARM"
        " 9 binary.\n\nr0: move pointer\nreturn: max PP for the given move, capped"
        " at 99",
    )

    MoveIsNotPhysical = Symbol(
        None,
        None,
        None,
        "Checks if a move isn't a physical move.\n\nr0: move ID\nreturn: bool",
    )

    TryPounce = Symbol(
        None,
        None,
        None,
        "Makes the target monster execute the Pounce action in a given direction if"
        " possible.\n\nIf the direction ID is 8, the target will pounce in the"
        " direction it's currently facing.\n\nr0: user entity pointer\nr1: target"
        " entity pointer\nr2: direction ID",
    )

    TryBlowAway = Symbol(
        None,
        None,
        None,
        "Blows away the target monster in a given direction if possible.\n\nr0: user"
        " entity pointer\nr1: target entity pointer\nr2: direction ID",
    )

    TryWarp = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Like DungeonRandOutcome, but specifically for user-target"
        " interactions.\n\nThis modifies the underlying random process depending on"
        " factors like Serene Grace, and whether or not either entity has"
        " fainted.\n\nr0: user entity pointer\nr1: target entity pointer\nr2: base"
        " success percentage (100*p). 0 is treated specially and guarantees success.",
    )

    DungeonRandOutcomeUserAction = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Updates the PP of any moves that were used by a monster, if PP should be"
        " consumed.\n\nr0: entity pointer\nr1: flag for whether or not PP should be"
        " consumed",
    )

    LowerSshort = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Deals damage from a move or item used by an attacking monster on a defending"
        " monster.\n\nr0: attacker pointer\nr1: defender pointer\nr2: move\nr3: damage"
        " multiplier (as a binary fixed-point number with 8 fraction bits)\nstack[0]:"
        " item ID\nreturn: amount of damage dealt",
    )

    CalcDamageProjectile = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Get the weather, as experienced by a specific entity.\n\nr0: entity"
        " pointer\nreturn: weather ID",
    )

    TryWeatherFormChange = Symbol(
        None,
        None,
        None,
        "Tries to change a monster into one of its weather-related alternative forms."
        " Applies to Castform and Cherrim, and checks for their unique"
        " abilities.\n\nr0: pointer to entity",
    )

    GetTile = Symbol(
        None,
        None,
        None,
        "Get the tile at some position. If the coordinates are out of bounds, returns a"
        " default tile.\n\nr0: x position\nr1: y position\nreturn: tile pointer",
    )

    GetTileSafe = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Checks if the current floor is a normal layout.\n\n'Normal' means any layout"
        " that is NOT one of the following:\n- Hidden stairs floors\n- Golden"
        " Chamber\n- Challenge Request floor\n- Outlaw hideout\n- Treasure Memo"
        " floor\n- Full-room fixed floors (ID < 0xA5) [0xA5 == Sealed"
        " Chamber]\n\nreturn: bool",
    )

    GenerateFloor = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Gets the terrain type of a tile.\n\nr0: tile pointer\nreturn: terrain ID",
    )

    DungeonRand100 = Symbol(
        None,
        None,
        None,
        "Compute a pseudorandom integer on the interval [0, 100) using the dungeon"
        " PRNG.\n\nreturn: pseudorandom integer",
    )

    FlagHallwayJunctions = Symbol(
        None,
        None,
        None,
        "Sets the junction flag (bit 3 of the terrain flags) on any hallway junction"
        " tiles in some range [x0, x1), [y0, y1). This leaves tiles within rooms"
        " untouched.\n\nA hallway tile is considered a junction if it has at least 3"
        " cardinal neighbors with open terrain.\n\nr0: x0\nr1: y0\nr2: x1\nr3: y1",
    )

    GenerateStandardFloor = Symbol(
        None,
        None,
        None,
        "Generate a standard floor with the given parameters.\n\nBroadly speaking, a"
        " standard floor is generated as follows:\n1. Generating the grid\n2. Creating"
        " a room or hallway anchor in each grid cell\n3. Creating hallways between grid"
        " cells\n4. Generating special features (maze room, Kecleon shop, Monster"
        " House, extra hallways, room imperfections, secondary structures)\n\nr0: grid"
        " size x\nr1: grid size y\nr2: floor properties",
    )

    GenerateOuterRingFloor = Symbol(
        None,
        None,
        None,
        "Generates a floor layout with a 4x2 grid of rooms, surrounded by an outer ring"
        " of hallways.\n\nr0: floor properties",
    )

    GenerateCrossroadsFloor = Symbol(
        None,
        None,
        None,
        "Generates a floor layout with a mesh of hallways on the interior 3x2 grid,"
        " surrounded by a boundary of rooms protruding from the interior like spikes,"
        " excluding the corner cells.\n\nr0: floor properties",
    )

    GenerateLineFloor = Symbol(
        None,
        None,
        None,
        "Generates a floor layout with 5 grid cells in a horizontal line.\n\nr0: floor"
        " properties",
    )

    GenerateCrossFloor = Symbol(
        None,
        None,
        None,
        "Generates a floor layout with 5 rooms arranged in a cross ('plus sign')"
        " formation.\n\nr0: floor properties",
    )

    GenerateBeetleFloor = Symbol(
        None,
        None,
        None,
        "Generates a floor layout in a 'beetle' formation, which is created by taking a"
        " 3x3 grid of rooms, connecting the rooms within each row, and merging the"
        " central column into one big room.\n\nr0: floor properties",
    )

    MergeRoomsVertically = Symbol(
        None,
        None,
        None,
        "Merges two vertically stacked rooms into one larger room.\n\nr0: x grid"
        " coordinate of the rooms to merge\nr1: y grid coordinate of the upper"
        " room\nr2: dy, where the lower room has a y grid coordinate of y+dy\nr3: grid"
        " to update",
    )

    GenerateOuterRoomsFloor = Symbol(
        None,
        None,
        None,
        "Generates a floor layout with a ring of rooms on the grid boundary and nothing"
        " in the interior.\n\nNote that this function is bugged, and won't properly"
        " connect all the rooms together for grid_size_x < 4.\n\nr0: grid size x\nr1:"
        " grid size y\nr2: floor properties",
    )

    IsNotFullFloorFixedRoom = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Generates a floor layout with just a large, one-room Monster House.\n\nThis is"
        " the default layout if dungeon generation fails.\n\nNo params.",
    )

    GenerateTwoRoomsWithMonsterHouseFloor = Symbol(
        None,
        None,
        None,
        "Generate a floor layout with two rooms (left and right), one of which is a"
        " Monster House.\n\nNo params.",
    )

    GenerateExtraHallways = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Get the grid cell positions for a given set of floor grid dimensions.\n\nr0:"
        " [output] pointer to array of the starting x coordinates of each grid"
        " column\nr1: [output] pointer to array of the starting y coordinates of each"
        " grid row\nr2: grid size x\nr3: grid size y",
    )

    InitDungeonGrid = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Attempt to generate room imperfections for each room in the floor layout, if"
        " enabled.\n\nEach room has a 40% chance of having imperfections if its grid"
        " cell is flagged to allow room imperfections. Imperfections are generated by"
        " randomly growing the walls of the room inwards for a certain number of"
        " iterations, starting from the corners.\n\nr0: grid to update\nr1: grid size"
        " x\nr2: grid size y",
    )

    CreateHallway = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Ensure the grid forms a connected graph (all valid cells are reachable) by"
        " adding hallways to unreachable grid cells.\n\nIf a grid cell cannot be"
        " connected for some reason, remove it entirely.\n\nr0: grid to update\nr1:"
        " grid size x\nr2: grid size y\nr3: array of the starting x coordinates of each"
        " grid column\nstack[0]: array of the starting y coordinates of each grid row",
    )

    SetTerrainObstacleChecked = Symbol(
        None,
        None,
        None,
        "Set the terrain of a specific tile to be an obstacle (wall or secondary"
        " terrain).\n\nSecondary terrain (water/lava) can only be placed in the"
        " specified room. If the tile room index does not match, a wall will be placed"
        " instead.\n\nr0: tile pointer\nr1: use secondary terrain flag (true for"
        " water/lava, false for wall)\nr2: room index",
    )

    FinalizeJunctions = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Possibly generate a maze room on the floor.\n\nA maze room will be generated"
        " with a probability determined by the maze room chance parameter. A maze will"
        " be generated in a random room that is valid, connected, has odd dimensions,"
        " and has no other features.\n\nr0: grid to update\nr1: grid size x\nr2: grid"
        " size y\nr3: maze room chance (percentage from 0-100)",
    )

    GenerateMaze = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Set spawn flag 5 (0b100000 or 0x20) on all tiles in a room.\n\nr0: grid cell",
    )

    IsNextToHallway = Symbol(
        None,
        None,
        None,
        "Checks if a tile position is either in a hallway or next to one.\n\nr0: x\nr1:"
        " y\nreturn: bool",
    )

    ResolveInvalidSpawns = Symbol(
        None,
        None,
        None,
        "Resolve invalid spawn flags on tiles.\n\nSpawn flags can be invalid due to"
        " terrain. For example, traps can't spawn on obstacles. Spawn flags can also be"
        " invalid due to multiple being set on a single tile, in which case one will"
        " take precedence. For example, stair spawns trump trap spawns.\n\nNo params.",
    )

    ConvertSecondaryTerrainToChasms = Symbol(
        None,
        None,
        None,
        "Converts all secondary terrain tiles (water/lava) to chasms.\n\nNo params.",
    )

    EnsureImpassableTilesAreWalls = Symbol(
        None,
        None,
        None,
        "Ensures all tiles with the impassable flag are walls.\n\nNo params.",
    )

    InitializeTile = Symbol(
        None, None, None, "Initialize a tile struct.\n\nr0: tile pointer"
    )

    ResetFloor = Symbol(
        None,
        None,
        None,
        "Resets the floor in preparation for a floor generation attempt.\n\nResets all"
        " tiles, resets the border to be impassable, and clears entity spawns.\n\nNo"
        " params.",
    )

    PosIsOutOfBounds = Symbol(
        None,
        None,
        None,
        "Checks if a position (x, y) is out of bounds on the map: !((0 <= x <= 55) &&"
        " (0 <= y <= 31)).\n\nr0: x\nr1: y\nreturn: bool",
    )

    ShuffleSpawnPositions = Symbol(
        None,
        None,
        None,
        "Randomly shuffle an array of spawn positions.\n\nr0: spawn position array"
        " containing bytes {x1, y1, x2, y2, ...}\nr1: number of (x, y) pairs in the"
        " spawn position array",
    )

    SpawnNonEnemies = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Set a specific tile to have secondary terrain (water/lava), but only if it's a"
        " passable wall.\n\nr0: tile pointer",
    )

    GenerateSecondaryTerrainFormations = Symbol(
        None,
        None,
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
        None,
        None,
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
        None, None, None, "Converts all wall tiles to chasms.\n\nNo params."
    )

    ResetInnerBoundaryTileRows = Symbol(
        None,
        None,
        None,
        "Reset the inner boundary tile rows (y == 1 and y == 30) to their initial state"
        " of all wall tiles, with impassable walls at the edges (x == 0 and x =="
        " 55).\n\nNo params.",
    )

    SpawnStairs = Symbol(
        None,
        None,
        None,
        "Spawn stairs at the given location.\n\nIf the hidden stairs flag is set,"
        " hidden stairs will be spawned instead of normal stairs.\n\nIf spawning normal"
        " stairs and the current floor is a rescue floor, the room containing the"
        " stairs will be converted into a Monster House.\n\nr0: position (two-byte"
        " array for {x, y})\nr1: dungeon generation info pointer (a field on the"
        " dungeon struct)\nr2: hidden stairs flag",
    )

    LoadFixedRoomData = Symbol(
        None,
        None,
        None,
        "Loads fixed room data from BALANCE/fixed.bin into the buffer pointed to by"
        " FIXED_ROOM_DATA_PTR.\n\nNo params.",
    )

    IsHiddenStairsFloor = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is either the Secret Bazaar or a Secret"
        " Room.\n\nreturn: bool",
    )

    HasHeldItem = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Checks if the current floor is an active mission destination of a given type"
        " (and any subtype).\n\nr0: mission type\nreturn: bool",
    )

    IsCurrentMissionTypeExact = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is an active mission destination of a given type"
        " and subtype.\n\nr0: mission type\nr1: mission subtype\nreturn: bool",
    )

    IsOutlawMonsterHouseFloor = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is a mission destination for a Monster House"
        " outlaw mission.\n\nreturn: bool",
    )

    IsGoldenChamber = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is a Golden Chamber floor.\n\nreturn: bool",
    )

    IsLegendaryChallengeFloor = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is a boss floor for a Legendary Challenge Letter"
        " mission.\n\nreturn: bool",
    )

    IsJirachiChallengeFloor = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is the boss floor in Star Cave Pit for Jirachi's"
        " Challenge Letter mission.\n\nreturn: bool",
    )

    IsDestinationFloorWithMonster = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Checks if the target enemy of the mission on the current floor has been"
        " defeated.\n\nreturn: bool",
    )

    SetMissionTargetEnemyDefeated = Symbol(
        None,
        None,
        None,
        "Set the flag for whether or not the target enemy of the current mission has"
        " been defeated.\n\nr0: new flag value",
    )

    IsDestinationFloorWithFixedRoom = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is a mission destination floor with a fixed"
        " room.\n\nThe entire floor can be a fixed room layout, or it can just contain"
        " a Sealed Chamber.\n\nreturn: bool",
    )

    GetItemToRetrieve = Symbol(
        None,
        None,
        None,
        "Get the ID of the item that needs to be retrieve on the current floor for a"
        " mission, if one exists.\n\nreturn: item ID",
    )

    GetItemToDeliver = Symbol(
        None,
        None,
        None,
        "Get the ID of the item that needs to be delivered to a mission client on the"
        " current floor, if one exists.\n\nreturn: item ID",
    )

    GetSpecialTargetItem = Symbol(
        None,
        None,
        None,
        "Get the ID of the special target item for a Sealed Chamber or Treasure Memo"
        " mission on the current floor.\n\nreturn: item ID",
    )

    IsDestinationFloorWithItem = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is a mission destination floor with a special"
        " item.\n\nThis excludes missions involving taking an item from an"
        " outlaw.\n\nreturn: bool",
    )

    IsDestinationFloorWithHiddenOutlaw = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is a mission destination floor with a 'hidden"
        " outlaw' that behaves like a normal enemy.\n\nreturn: bool",
    )

    IsDestinationFloorWithFleeingOutlaw = Symbol(
        None,
        None,
        None,
        "Checks if the current floor is a mission destination floor with a 'fleeing"
        " outlaw' that runs away.\n\nreturn: bool",
    )

    GetMissionTargetEnemy = Symbol(
        None,
        None,
        None,
        "Get the monster ID of the target enemy to be defeated on the current floor for"
        " a mission, if one exists.\n\nreturn: monster ID",
    )

    GetMissionEnemyMinionGroup = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Checks if a given floor is a mission destination with a special monster,"
        " either a target to rescue or an enemy to defeat.\n\nMission types with a"
        " monster on the destination floor:\n- Rescue client\n- Rescue target\n- Escort"
        " to target\n- Deliver item\n- Search for target\n- Take item from outlaw\n-"
        " Arrest outlaw\n- Challenge Request\n\nr0: mission destination info"
        " pointer\nreturn: bool",
    )

    LogMessageByIdWithPopupCheckUser = Symbol(
        None,
        None,
        None,
        "Logs a message in the message log alongside a message popup, if the user"
        " hasn't fainted.\n\nr0: user entity pointer\nr1: message ID",
    )

    LogMessageWithPopupCheckUser = Symbol(
        None,
        None,
        None,
        "Logs a message in the message log alongside a message popup, if the user"
        " hasn't fainted.\n\nr0: user entity pointer\nr1: message string",
    )

    LogMessageByIdQuiet = Symbol(
        None,
        None,
        None,
        "Logs a message in the message log (but without a message popup).\n\nr0: user"
        " entity pointer\nr1: message ID",
    )

    LogMessageQuiet = Symbol(
        None,
        None,
        None,
        "Logs a message in the message log (but without a message popup).\n\nr0: user"
        " entity pointer\nr1: message string",
    )

    LogMessageByIdWithPopupCheckUserTarget = Symbol(
        None,
        None,
        None,
        "Logs a message in the message log alongside a message popup, if some user"
        " check passes and the target hasn't fainted.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: message ID",
    )

    LogMessageWithPopupCheckUserTarget = Symbol(
        None,
        None,
        None,
        "Logs a message in the message log alongside a message popup, if some user"
        " check passes and the target hasn't fainted.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: message string",
    )

    LogMessageByIdQuietCheckUserTarget = Symbol(
        None,
        None,
        None,
        "Logs a message in the message log (but without a message popup), if some user"
        " check passes and the target hasn't fainted.\n\nr0: user entity pointer\nr1:"
        " target entity pointer\nr2: message ID",
    )

    LogMessageByIdWithPopupCheckUserUnknown = Symbol(
        None,
        None,
        None,
        "Logs a message in the message log alongside a message popup, if the user"
        " hasn't fainted and some other unknown check.\n\nr0: user entity pointer\nr1:"
        " ?\nr2: message ID",
    )

    LogMessageByIdWithPopup = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Logs a message in the message log.\n\nr0: user entity pointer\nr1: message"
        " string\nr2: bool, whether or not to present a message popup",
    )

    LogMessageById = Symbol(
        None,
        None,
        None,
        "Logs a message in the message log.\n\nr0: user entity pointer\nr1: message"
        " ID\nr2: bool, whether or not to present a message popup",
    )

    OpenMessageLog = Symbol(
        None, None, None, "Opens the message log window.\n\nr0: ?\nr1: ?"
    )

    RunDungeonMode = Symbol(
        None,
        None,
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
        None,
        None,
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


class NaItcmOverlay29Data:
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


class NaItcmOverlay29Section:
    name = "overlay29"
    description = (
        "The dungeon engine.\n\nThis is the 'main' overlay of dungeon mode. It controls"
        " most things that happen in a Mystery Dungeon, such as dungeon layout"
        " generation, dungeon menus, enemy AI, and generally just running each turn"
        " while within a dungeon."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay29Functions
    data = NaItcmOverlay29Data


class NaItcmOverlay11Functions:
    FuncThatCallsCommandParsing = Symbol(None, None, None, "")

    ScriptCommandParsing = Symbol(None, None, None, "")

    SsbLoad2 = Symbol(None, None, None, "")

    StationLoadHanger = Symbol(None, None, None, "")

    ScriptStationLoadTalk = Symbol(None, None, None, "")

    SsbLoad1 = Symbol(None, None, None, "")

    ScriptSpecialProcessCall = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Returns an entry from RECRUITMENT_TABLE_SPECIES.\n\nNote: This indexes without"
        " doing bounds checking.\n\nr0: index into RECRUITMENT_TABLE_SPECIES\nreturn:"
        " enum monster_id",
    )

    PrepareMenuAcceptTeamMember = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_PREPARE_MENU_ACCEPT_TEAM_MEMBER (see"
        " ScriptSpecialProcessCall).\n\nr0: index into RECRUITMENT_TABLE_SPECIES",
    )

    InitRandomNpcJobs = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_INIT_RANDOM_NPC_JOBS (see"
        " ScriptSpecialProcessCall).\n\nr0: job type? 0 is a random NPC job, 1 is a"
        " bottle mission\nr1: ?",
    )

    GetRandomNpcJobType = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_GET_RANDOM_NPC_JOB_TYPE (see"
        " ScriptSpecialProcessCall).\n\nreturn: job type?",
    )

    GetRandomNpcJobSubtype = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_GET_RANDOM_NPC_JOB_SUBTYPE (see"
        " ScriptSpecialProcessCall).\n\nreturn: job subtype?",
    )

    GetRandomNpcJobStillAvailable = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_GET_RANDOM_NPC_JOB_STILL_AVAILABLE (see"
        " ScriptSpecialProcessCall).\n\nreturn: bool",
    )

    AcceptRandomNpcJob = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_ACCEPT_RANDOM_NPC_JOB (see"
        " ScriptSpecialProcessCall).\n\nreturn: bool",
    )

    GroundMainLoop = Symbol(
        None,
        None,
        None,
        "Appears to be the main loop for ground mode.\n\nBased on debug print"
        " statements and general code structure, it seems contain a core loop, and"
        " dispatches to various functions in response to different events.\n\nr0: mode,"
        " which is stored globally and used in switch statements for dispatch\nreturn:"
        " return code",
    )

    GetAllocArenaGround = Symbol(
        None,
        None,
        None,
        "The GetAllocArena function used for ground mode. See SetMemAllocatorParams for"
        " more information.\n\nr0: initial memory arena pointer, or null\nr1: flags"
        " (see MemAlloc)\nreturn: memory arena pointer, or null",
    )

    GetFreeArenaGround = Symbol(
        None,
        None,
        None,
        "The GetFreeArena function used for ground mode. See SetMemAllocatorParams for"
        " more information.\n\nr0: initial memory arena pointer, or null\nr1: pointer"
        " to free\nreturn: memory arena pointer, or null",
    )

    GroundMainReturnDungeon = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_RETURN_DUNGEON (see ScriptSpecialProcessCall).\n\nNo"
        " params.",
    )

    GroundMainNextDay = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_NEXT_DAY (see ScriptSpecialProcessCall).\n\nNo"
        " params.",
    )

    JumpToTitleScreen = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_JUMP_TO_TITLE_SCREEN and SPECIAL_PROC_0x1A (see"
        " ScriptSpecialProcessCall).\n\nr0: int, argument value for"
        " SPECIAL_PROC_JUMP_TO_TITLE_SCREEN and -1 for SPECIAL_PROC_0x1A\nreturn: bool"
        " (but note that the special process ignores this and always returns 0)",
    )

    ReturnToTitleScreen = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_RETURN_TO_TITLE_SCREEN (see"
        " ScriptSpecialProcessCall).\n\nr0: fade duration\nreturn: bool (but note that"
        " the special process ignores this and always returns 0)",
    )

    ScriptSpecialProcess0x16 = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_0x16 (see ScriptSpecialProcessCall).\n\nr0: bool",
    )

    SprintfStatic = Symbol(
        None,
        None,
        None,
        "Statically defined copy of sprintf(3) in overlay 11. See arm9.yml for more"
        " information.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )

    StatusUpdate = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_STATUS_UPDATE (see ScriptSpecialProcessCall).\n\nNo"
        " params.",
    )


class NaItcmOverlay11Data:
    SCRIPT_OP_CODES = Symbol(
        None,
        None,
        None,
        "Table of opcodes for the script engine. There are 383 8-byte entries.\n\nThese"
        " opcodes underpin the various ExplorerScript functions you can call in the"
        " SkyTemple SSB debugger.\n\ntype: struct script_opcode_table",
    )

    C_ROUTINES = Symbol(
        None,
        None,
        None,
        "Common routines used within the unionall.ssb script (the master script). There"
        " are 701 8-byte entries.\n\nThese routines underpin the ExplorerScript"
        " coroutines you can call in the SkyTemple SSB debugger.\n\ntype: struct"
        " common_routine_table",
    )

    OBJECTS = Symbol(
        None,
        None,
        None,
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


class NaItcmOverlay11Section:
    name = "overlay11"
    description = (
        "The script engine.\n\nThis is the 'main' overlay of ground mode. The script"
        " engine is what runs the ground mode scripts contained in the SCRIPT folder,"
        " which are written in a custom scripting language. These scripts encode things"
        " like cutscenes, screen transitions, ground mode events, and tons of other"
        " things related to ground mode."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay11Functions
    data = NaItcmOverlay11Data


class NaItcmOverlay25Functions:
    pass


class NaItcmOverlay25Data:
    APPRAISAL_MENU_CONFIRM = Symbol(None, None, None, "")

    APPRAISAL_MAIN_MENU = Symbol(None, None, None, "")

    APPRAISAL_SUBMENU = Symbol(None, None, None, "")


class NaItcmOverlay25Section:
    name = "overlay25"
    description = "Controls Xatu Appraisal."
    loadaddress = None
    length = None
    functions = NaItcmOverlay25Functions
    data = NaItcmOverlay25Data


class NaItcmArm9Functions:
    InitMemAllocTable = Symbol(
        None,
        None,
        None,
        "Initializes MEMORY_ALLOCATION_TABLE.\n\nSets up the default memory arena, sets"
        " the default memory allocator parameters (calls SetMemAllocatorParams(0, 0)),"
        " and does some other stuff.\n\nNo params.",
    )

    SetMemAllocatorParams = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "The default function for retrieving the arena for memory allocations. This"
        " function always just returns the initial arena pointer.\n\nr0: initial memory"
        " arena pointer, or null\nr1: flags (see MemAlloc)\nreturn: memory arena"
        " pointer, or null",
    )

    GetFreeArenaDefault = Symbol(
        None,
        None,
        None,
        "The default function for retrieving the arena for memory freeing. This"
        " function always just returns the initial arena pointer.\n\nr0: initial memory"
        " arena pointer, or null\nr1: pointer to free\nreturn: memory arena pointer, or"
        " null",
    )

    InitMemArena = Symbol(
        None,
        None,
        None,
        "Initializes a new memory arena with the given specifications, and records it"
        " in the global MEMORY_ALLOCATION_TABLE.\n\nr0: arena struct to be"
        " initialized\nr1: memory region to be owned by the arena, as {pointer,"
        " length}\nr2: pointer to block metadata array for the arena to use\nr3:"
        " maximum number of blocks that the arena can hold",
    )

    MemAllocFlagsToBlockType = Symbol(
        None,
        None,
        None,
        "Converts the internal alloc flags bitfield (struct mem_block field 0x4) to the"
        " block type bitfield (struct mem_block field 0x0).\n\nr0: internal alloc"
        " flags\nreturn: block type flags",
    )

    FindAvailableMemBlock = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Allocates some memory on the heap, returning a pointer to the starting"
        " address.\n\nMemory allocation is done with region-based memory management."
        " See MEMORY_ALLOCATION_TABLE for more information.\n\nThis function is just a"
        " wrapper around MemLocateSet.\n\nr0: length in bytes\nr1: flags (see the"
        " comment on struct mem_block::user_flags)\nreturn: pointer",
    )

    MemFree = Symbol(
        None,
        None,
        None,
        "Frees heap-allocated memory.\n\nThis function is just a wrapper around"
        " MemLocateUnset.\n\nr0: pointer",
    )

    MemArenaAlloc = Symbol(
        None,
        None,
        None,
        "Allocates some memory on the heap and creates a new global memory arena with"
        " it.\n\nThe actual allocation part works similarly to the normal"
        " MemAlloc.\n\nr0: desired parent memory arena, or null\nr1: length of the"
        " arena in bytes\nr2: maximum number of blocks that the arena can hold\nr3:"
        " flags (see MemAlloc)\nreturn: memory arena pointer",
    )

    CreateMemArena = Symbol(
        None,
        None,
        None,
        "Creates a new memory arena within a given block of memory.\n\nThis is"
        " essentially a wrapper around InitMemArena, accounting for the space needed by"
        " the arena metadata.\n\nr0: memory region in which to create the arena, as"
        " {pointer, length}\nr1: maximum number of blocks that the arena can"
        " hold\nreturn: memory arena pointer",
    )

    MemLocateSet = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "The implementation for MemFree.\n\nAt a high level, memory is freed by"
        " locating the pointer in its memory arena (searching block-by-block) and"
        " emptying the block so it's available for future allocations, and merging it"
        " with neighboring blocks if they're available.\n\nr0: desired memory arena for"
        " freeing, or null (MemFree passes null)\nr1: pointer to free",
    )

    RoundUpDiv256 = Symbol(
        None,
        None,
        None,
        "Divide a number by 256 and round up to the nearest integer.\n\nr0:"
        " number\nreturn: number // 256",
    )

    MultiplyByFixedPoint = Symbol(
        None,
        None,
        None,
        "Multiply a signed integer x by a signed binary fixed-point multiplier (8"
        " fraction bits).\n\nr0: x\nr1: multiplier\nreturn: x * multiplier",
    )

    UMultiplyByFixedPoint = Symbol(
        None,
        None,
        None,
        "Multiplies an unsigned integer x by an unsigned binary fixed-point multiplier"
        " (8 fraction bits).\n\nr0: x\nr1: multiplier\nreturn: x * multiplier",
    )

    GetRngSeed = Symbol(None, None, None, "Get the current value of PRNG_SEQUENCE_NUM.")

    SetRngSeed = Symbol(
        None, None, None, "Seed PRNG_SEQUENCE_NUM to a given value.\n\nr0: seed"
    )

    Rand16Bit = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Compute a pseudorandom integer under a given maximum value using the"
        " general-purpose PRNG.\n\nThis function relies on a single call to Rand16Bit."
        " Even though it takes a 32-bit integer as input, the number of unique outcomes"
        " is capped at 2^16.\n\nr0: high\nreturn: pseudorandom integer on the interval"
        " [0, high - 1]",
    )

    RandRange = Symbol(
        None,
        None,
        None,
        "Compute a pseudorandom value between two integers using the general-purpose"
        " PRNG.\n\nThis function relies on a single call to Rand16Bit. Even though it"
        " takes 32-bit integers as input, the number of unique outcomes is capped at"
        " 2^16.\n\nr0: x\nr1: y\nreturn: pseudorandom integer on the interval [x, y"
        " - 1]",
    )

    Rand32Bit = Symbol(
        None,
        None,
        None,
        "Computes a random 32-bit integer using the general-purpose PRNG. The upper and"
        " lower 16 bits are each generated with a separate call to Rand16Bit (so this"
        " function advances the PRNG twice).\n\nreturn: pseudorandom int on the"
        " interval [0, 4294967295]",
    )

    RandIntSafe = Symbol(
        None,
        None,
        None,
        "Same as RandInt, except explicitly masking out the upper 16 bits of the output"
        " from Rand16Bit (which should be zero anyway).\n\nr0: high\nreturn:"
        " pseudorandom integer on the interval [0, high - 1]",
    )

    RandRangeSafe = Symbol(
        None,
        None,
        None,
        "Like RandRange, except reordering the inputs as needed, and explicitly masking"
        " out the upper 16 bits of the output from Rand16Bit (which should be zero"
        " anyway).\n\nr0: x\nr1: y\nreturn: pseudorandom integer on the interval"
        " [min(x, y), max(x, y) - 1]",
    )

    WaitForever = Symbol(
        None,
        None,
        None,
        "Sets some program state and calls WaitForInterrupt in an infinite"
        " loop.\n\nThis is called on fatal errors to hang the program"
        " indefinitely.\n\nNo params.",
    )

    InitMemAllocTableVeneer = Symbol(
        None,
        None,
        None,
        "Likely a linker-generated veneer for InitMemAllocTable.\n\nSee"
        " https://developer.arm.com/documentation/dui0474/k/image-structure-and-generation/linker-generated-veneers/what-is-a-veneer-\n\nNo"
        " params.",
    )

    MemZero = Symbol(None, None, None, "Zeroes a buffer.\n\nr0: ptr\nr1: len")

    MemcpySimple = Symbol(
        None,
        None,
        None,
        "A simple implementation of the memcpy(3) C library function.\n\nThis function"
        " was probably manually implemented by the developers. See Memcpy for what's"
        " probably the real libc function.\n\nThis function copies from src to dst in"
        " backwards byte order, so this is safe to call for overlapping src and dst if"
        " src <= dst.\n\nr0: dest\nr1: src\nr2: n",
    )

    TaskProcBoot = Symbol(
        None,
        None,
        None,
        "Probably related to booting the game?\n\nThis function prints the debug"
        " message 'task proc boot'.\n\nNo params.",
    )

    EnableAllInterrupts = Symbol(
        None,
        None,
        None,
        "Sets the Interrupt Master Enable (IME) register to 1, which enables all CPU"
        " interrupts (if enabled in the Interrupt Enable (IE) register).\n\nSee"
        " https://problemkaputt.de/gbatek.htm#dsiomaps.\n\nreturn: old value in the IME"
        " register",
    )

    GetTime = Symbol(
        None,
        None,
        None,
        "Seems to get the current (system?) time as an IEEE 754 floating-point"
        " number.\n\nreturn: current time (maybe in seconds?)",
    )

    DisableAllInterrupts = Symbol(
        None,
        None,
        None,
        "Sets the Interrupt Master Enable (IME) register to 0, which disables all CPU"
        " interrupts (even if enabled in the Interrupt Enable (IE) register).\n\nSee"
        " https://problemkaputt.de/gbatek.htm#dsiomaps.\n\nreturn: old value in the IME"
        " register",
    )

    SoundResume = Symbol(
        None,
        None,
        None,
        "Probably resumes the sound player if paused?\n\nThis function prints the debug"
        " string 'sound resume'.",
    )

    CardPullOutWithStatus = Symbol(
        None,
        None,
        None,
        "Probably aborts the program with some status code? It seems to serve a similar"
        " purpose to the exit(3) function.\n\nThis function prints the debug string"
        " 'card pull out %d' with the status code.\n\nr0: status code",
    )

    CardPullOut = Symbol(
        None,
        None,
        None,
        "Sets some global flag that probably triggers system exit?\n\nThis function"
        " prints the debug string 'card pull out'.\n\nNo params.",
    )

    CardBackupError = Symbol(
        None,
        None,
        None,
        "Sets some global flag that maybe indicates a save error?\n\nThis function"
        " prints the debug string 'card backup error'.\n\nNo params.",
    )

    HaltProcessDisp = Symbol(
        None,
        None,
        None,
        "Maybe halts the process display?\n\nThis function prints the debug string"
        " 'halt process disp %d' with the status code.\n\nr0: status code",
    )

    OverlayIsLoaded = Symbol(
        None,
        None,
        None,
        "Checks if an overlay with a certain group ID is currently loaded.\n\nSee the"
        " LOADED_OVERLAY_GROUP_* data symbols or enum overlay_group_id in the C headers"
        " for a mapping between group ID and overlay number.\n\nr0: group ID of the"
        " overlay to check. A group ID of 0 denotes no overlay, and the return value"
        " will always be true in this case.\nreturn: bool",
    )

    LoadOverlay = Symbol(
        None,
        None,
        None,
        "Loads an overlay from ROM by its group ID.\n\nSee the LOADED_OVERLAY_GROUP_*"
        " data symbols or enum overlay_group_id in the C headers for a mapping between"
        " group ID and overlay number.\n\nr0: group ID of the overlay to load",
    )

    UnloadOverlay = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Clamps the absolute values in a two-component integer array.\n\nGiven an"
        " integer array [x, y] and a maximum absolute value M, clamps each element of"
        " the array to M such that the output array is [min(max(x, -M), M), min(max(y,"
        " -M), M)].\n\nr0: 2-element integer array, will be mutated\nr1: max absolute"
        " value",
    )

    KeyWaitInit = Symbol(
        None,
        None,
        None,
        "Implements (most of?) SPECIAL_PROC_KEY_WAIT_INIT (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    DataTransferInit = Symbol(
        None,
        None,
        None,
        "Initializes data transfer mode to get data from the ROM cartridge.\n\nNo"
        " params.",
    )

    DataTransferStop = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Opens a file from the ROM file system at the given path, sort of like C's"
        " fopen(3) library function.\n\nr0: file_stream pointer\nr1: file path string",
    )

    FileGetSize = Symbol(
        None,
        None,
        None,
        "Gets the size of an open file.\n\nr0: file_stream pointer\nreturn: file size",
    )

    FileRead = Symbol(
        None,
        None,
        None,
        "Reads the contents of a file into the given buffer, and moves the file cursor"
        " accordingly.\n\nData transfer mode must have been initialized (with"
        " DataTransferInit) prior to calling this function. This function looks like"
        " it's doing something akin to calling read(2) or fread(3) in a loop until all"
        " the bytes have been successfully read.\n\nr0: file_stream pointer\nr1:"
        " [output] buffer\nr2: number of bytes to read\nreturn: number of bytes read",
    )

    FileSeek = Symbol(
        None,
        None,
        None,
        "Sets a file stream's position indicator.\n\nThis function has the a similar"
        " API to the fseek(3) library function from C, including using the same codes"
        " for the `whence` parameter:\n- SEEK_SET=0\n- SEEK_CUR=1\n- SEEK_END=2\n\nr0:"
        " file_stream pointer\nr1: offset\nr2: whence",
    )

    FileClose = Symbol(
        None,
        None,
        None,
        "Closes a file.\n\nData transfer mode must have been initialized (with"
        " DataTransferInit) prior to calling this function.\n\nNote: It is possible to"
        " keep a file stream open even if data transfer mode has been stopped, in which"
        " case the file stream can be used again if data transfer mode is"
        " reinitialized.\n\nr0: file_stream pointer",
    )

    LoadFileFromRom = Symbol(
        None,
        None,
        None,
        "Loads a file from ROM by filepath into a heap-allocated buffer.\n\nr0:"
        " [output] pointer to an IO struct {ptr, len}\nr1: file path string"
        " pointer\nr2: flags",
    )

    GetDebugFlag1 = Symbol(None, None, None, "Just returns 0 in the final binary.")

    SetDebugFlag1 = Symbol(None, None, None, "A no-op in the final binary.")

    AppendProgPos = Symbol(
        None,
        None,
        None,
        "Write a base message into a string and append the file name and line number to"
        " the end in the format 'file = '%s'  line = %5d\n'.\n\nIf no program position"
        " info is given, 'ProgPos info NULL\n' is appended instead.\n\nr0: [output]"
        " str\nr1: program position info\nr2: base message\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )

    DebugPrintTrace = Symbol(
        None,
        None,
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

    GetDebugFlag2 = Symbol(None, None, None, "Just returns 0 in the final binary.")

    SetDebugFlag2 = Symbol(None, None, None, "A no-op in the final binary.")

    DebugPrint = Symbol(
        None,
        None,
        None,
        "Would log a printf format string in the debug binary. A no-op in the final"
        " binary.\n\nr0: log level\nr1: format\n...: variadic",
    )

    FatalError = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Sets the amount of money the player is carrying, clamping the value to the"
        " range [0, MAX_MONEY_CARRIED].\n\nr0: new value",
    )

    IsBagFull = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_IS_BAG_FULL (see ScriptSpecialProcessCall).\n\nreturn:"
        " bool",
    )

    CountItemTypeInBag = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_COUNT_ITEM_TYPE_IN_BAG (see"
        " ScriptSpecialProcessCall).\n\nr0: item ID\nreturn: number of items of the"
        " specified ID in the bag",
    )

    AddItemToBag = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_ADD_ITEM_TO_BAG (see ScriptSpecialProcessCall).\n\nr0:"
        " pointer to an owned_item\nreturn: bool",
    )

    ScriptSpecialProcess0x39 = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_0x39 (see ScriptSpecialProcessCall).\n\nreturn: bool",
    )

    CountItemTypeInStorage = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_COUNT_ITEM_TYPE_IN_STORAGE (see"
        " ScriptSpecialProcessCall).\n\nr0: pointer to an owned_item\nreturn: number of"
        " items of the specified ID in storage",
    )

    RemoveItemsTypeInStorage = Symbol(
        None,
        None,
        None,
        "Probably? Implements SPECIAL_PROC_0x2A (see ScriptSpecialProcessCall).\n\nr0:"
        " pointer to an owned_item\nreturn: bool",
    )

    AddItemToStorage = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_ADD_ITEM_TO_STORAGE (see"
        " ScriptSpecialProcessCall).\n\nr0: pointer to an owned_item\nreturn: bool",
    )

    SetMoneyStored = Symbol(
        None,
        None,
        None,
        "Sets the amount of money the player has stored in the Duskull Bank, clamping"
        " the value to the range [0, MAX_MONEY_STORED].\n\nr0: new value",
    )

    GetExclusiveItemOffset = Symbol(
        None,
        None,
        None,
        "Gets the exclusive item offset, which is the item ID relative to that of the"
        " first exclusive item, the Prism Ruff.\n\nr0: item ID\nreturn: offset",
    )

    ApplyExclusiveItemStatBoosts = Symbol(
        None,
        None,
        None,
        "Applies stat boosts from an exclusive item.\n\nr0: item ID\nr1: pointer to"
        " attack stat to modify\nr2: pointer to special attack stat to modify\nr3:"
        " pointer to defense stat to modify\nstack[0]: pointer to special defense stat"
        " to modify",
    )

    SetExclusiveItemEffect = Symbol(
        None,
        None,
        None,
        "Sets the bit for an exclusive item effect.\n\nr0: pointer to the effects"
        " bitvector to modify\nr1: exclusive item effect ID",
    )

    ExclusiveItemEffectFlagTest = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Gets the maximum PP for a given move.\n\nr0: move pointer\nreturn: max PP for"
        " the given move, capped at 99",
    )

    GetMoveCritChance = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Gets a move's category (physical, special, status).\n\nr0: move ID\nreturn:"
        " move category enum",
    )

    LoadWteFromRom = Symbol(
        None,
        None,
        None,
        "Loads a SIR0-wrapped WTE file from ROM, and returns a handle to it\n\nr0:"
        " [output] pointer to wte handle\nr1: file path string\nr2: load file flags",
    )

    LoadWteFromFileDirectory = Symbol(
        None,
        None,
        None,
        "Loads a SIR0-wrapped WTE file from a file directory, and returns a handle to"
        " it\n\nr0: [output] pointer to wte handle\nr1: file directory id\nr2: file"
        " index\nr3: malloc flags",
    )

    UnloadWte = Symbol(
        None,
        None,
        None,
        "Frees the buffer used to store the WTE data in the handle, and sets both"
        " pointers to null\n\nr0: pointer to wte handle",
    )

    HandleSir0Translation = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Gets the language type.\n\nThis is the value backing the special LANGUAGE_TYPE"
        " script variable.\n\nreturn: language type",
    )

    GetLanguage = Symbol(
        None,
        None,
        None,
        "Gets the single-byte language ID of the current program.\n\nThe language ID"
        " appears to be used to index some global tables.\n\nreturn: language ID",
    )

    PreprocessString = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "A simple implementation of the strcpy(3) C library function.\n\nThis function"
        " was probably manually implemented by the developers. See Strcpy for what's"
        " probably the real libc function.\n\nr0: dest\nr1: src",
    )

    StrncpySimple = Symbol(
        None,
        None,
        None,
        "A simple implementation of the strncpy(3) C library function.\n\nThis function"
        " was probably manually implemented by the developers. See Strncpy for what's"
        " probably the real libc function.\n\nr0: dest\nr1: src\nr2: n",
    )

    StringFromMessageId = Symbol(
        None,
        None,
        None,
        "Gets the string corresponding to a given message ID.\n\nr0: message"
        " ID\nreturn: string from the string files with the given message ID",
    )

    SetScreenWindowsColor = Symbol(
        None,
        None,
        None,
        "Sets the palette of the frames of windows in the specified screen\n\nr0:"
        " palette index\nr1: is upper screen",
    )

    SetBothScreensWindowsColor = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Implements SPECIAL_PROC_INIT_MAIN_TEAM_AFTER_QUIZ (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x3 = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_0x3 (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x4 = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_0x4 (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    NoteSaveBase = Symbol(
        None,
        None,
        None,
        "Probably related to saving or quicksaving?\n\nThis function prints the debug"
        " message 'NoteSave Base %d %d' with some values. It's also the only place"
        " where GetRngSeed is called.\n\nr0: possibly a flag/code that controls the"
        " type of save file to generate?\nothers: ?\nreturn: status code",
    )

    NoteLoadBase = Symbol(
        None,
        None,
        None,
        "Probably related to loading a save file or quicksave?\n\nThis function prints"
        " the debug message 'NoteLoad Base %d' with some value. It's also the only"
        " place where SetRngSeed is called.\n\nreturn: status code",
    )

    GetGameMode = Symbol(
        None, None, None, "Gets the value of GAME_MODE.\n\nreturn: game mode"
    )

    InitScriptVariableValues = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Zero-initialize the values of the given script variable.\n\nr0: pointer to the"
        " local variable table (only needed if id >= VAR_LOCAL0)\nr1: script"
        " variable ID",
    )

    LoadScriptVariableRaw = Symbol(
        None,
        None,
        None,
        "Loads a script variable descriptor for a given ID.\n\nr0: [output] script"
        " variable descriptor pointer\nr1: pointer to the local variable table (doesn't"
        " need to be valid; just controls the output value pointer)\nr2: script"
        " variable ID",
    )

    LoadScriptVariableValue = Symbol(
        None,
        None,
        None,
        "Loads the value of a script variable.\n\nr0: pointer to the local variable"
        " table (only needed if id >= VAR_LOCAL0)\nr1: script variable ID\nreturn:"
        " value",
    )

    LoadScriptVariableValueAtIndex = Symbol(
        None,
        None,
        None,
        "Loads the value of a script variable at some index (for script variables that"
        " are arrays).\n\nr0: pointer to the local variable table (only needed if id >="
        " VAR_LOCAL0)\nr1: script variable ID\nr2: value index for the given script"
        " var\nreturn: value",
    )

    SaveScriptVariableValue = Symbol(
        None,
        None,
        None,
        "Saves the given value to a script variable.\n\nr0: pointer to local variable"
        " table (only needed if id >= VAR_LOCAL0)\nr1: script variable ID\nr2: value to"
        " save",
    )

    SaveScriptVariableValueAtIndex = Symbol(
        None,
        None,
        None,
        "Saves the given value to a script variable at some index (for script variables"
        " that are arrays).\n\nr0: pointer to local variable table (only needed if id"
        " >= VAR_LOCAL0)\nr1: script variable ID\nr2: value index for the given script"
        " var\nr3: value to save",
    )

    LoadScriptVariableValueSum = Symbol(
        None,
        None,
        None,
        "Loads the sum of all values of a given script variable (for script variables"
        " that are arrays).\n\nr0: pointer to the local variable table (only needed if"
        " id >= VAR_LOCAL0)\nr1: script variable ID\nreturn: sum of values",
    )

    LoadScriptVariableValueBytes = Symbol(
        None,
        None,
        None,
        "Loads some number of bytes from the value of a given script variable.\n\nr0:"
        " script variable ID\nr1: [output] script variable value bytes\nr2: number of"
        " bytes to load",
    )

    SaveScriptVariableValueBytes = Symbol(
        None,
        None,
        None,
        "Saves some number of bytes to the given script variable.\n\nr0: script"
        " variable ID\nr1: bytes to save\nr2: number of bytes",
    )

    ScriptVariablesEqual = Symbol(
        None,
        None,
        None,
        "Checks if two script variables have equal values. For arrays, compares"
        " elementwise for the length of the first variable.\n\nr0: pointer to the local"
        " variable table (only needed if id >= VAR_LOCAL0)\nr1: script variable ID"
        " 1\nr2: script variable ID 2\nreturn: true if values are equal, false"
        " otherwise",
    )

    EventFlagBackup = Symbol(
        None,
        None,
        None,
        "Saves event flag script variables (see the code for an exhaustive list) to"
        " their respective BACKUP script variables, but only in certain game"
        " modes.\n\nThis function prints the debug string 'EventFlag BackupGameMode %d'"
        " with the game mode.\n\nNo params.",
    )

    DumpScriptVariableValues = Symbol(
        None,
        None,
        None,
        "Runs EventFlagBackup, then copies the script variable values table"
        " (SCRIPT_VARS_VALUES) to the given pointer.\n\nr0: destination pointer for the"
        " data dump\nreturn: always 1",
    )

    RestoreScriptVariableValues = Symbol(
        None,
        None,
        None,
        "Restores the script variable values table (SCRIPT_VARS_VALUES) with the given"
        " data. The source data is assumed to be exactly 1024 bytes in length.\n\nr0:"
        " raw data to copy to the values table\nreturn: whether the restored value for"
        " VAR_VERSION is equal to its default value",
    )

    InitScenarioScriptVars = Symbol(
        None,
        None,
        None,
        "Initializes most of the SCENARIO_* script variables (except"
        " SCENARIO_TALK_BIT_FLAG for some reason). Also initializes the PLAY_OLD_GAME"
        " variable.\n\nNo params.",
    )

    SetScenarioScriptVar = Symbol(
        None,
        None,
        None,
        "Sets the given SCENARIO_* script variable with a given pair of values [val0,"
        " val1].\n\nIn the special case when the ID is VAR_SCENARIO_MAIN, and the set"
        " value is different from the old one, the REQUEST_CLEAR_COUNT script variable"
        " will be set to 0.\n\nr0: script variable ID\nr1: val0\nr2: val1",
    )

    GetSpecialEpisodeType = Symbol(
        None,
        None,
        None,
        "Gets the special episode type from the SPECIAL_EPISODE_TYPE script"
        " variable.\n\nreturn: special episode type",
    )

    ScenarioFlagBackup = Symbol(
        None,
        None,
        None,
        "Saves scenario flag script variables (SCENARIO_SELECT, SCENARIO_MAIN_BIT_FLAG)"
        " to their respective BACKUP script variables, but only in certain game"
        " modes.\n\nThis function prints the debug string 'ScenarioFlag BackupGameMode"
        " %d' with the game mode.\n\nNo params.",
    )

    InitWorldMapScriptVars = Symbol(
        None,
        None,
        None,
        "Initializes the WORLD_MAP_* script variable values (IDs 0x55-0x57).\n\nNo"
        " params.",
    )

    InitDungeonListScriptVars = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Always returns true.\n\nThis function seems to be a debug switch that the"
        " developers may have used to disable the random enemy spawn. \nIf it returned"
        " false, the call to SpawnMonster inside TrySpawnMonsterAndTickSpawnCounter"
        " would not be executed.\n\nreturn: bool (always true)",
    )

    SetAdventureLogStructLocation = Symbol(
        None,
        None,
        None,
        "Sets the location of the adventure log struct in memory.\n\nSets it in a"
        " static memory location (At 0x22AB69C [US], 0x22ABFDC [EU], 0x22ACE58"
        " [JP])\n\nNo params.",
    )

    SetAdventureLogDungeonFloor = Symbol(
        None,
        None,
        None,
        "Sets the current dungeon floor pair.\n\nr0: struct dungeon_floor_pair",
    )

    GetAdventureLogDungeonFloor = Symbol(
        None,
        None,
        None,
        "Gets the current dungeon floor pair.\n\nreturn: struct dungeon_floor_pair",
    )

    ClearAdventureLogStruct = Symbol(
        None, None, None, "Clears the adventure log structure.\n\nNo params."
    )

    SetAdventureLogCompleted = Symbol(
        None,
        None,
        None,
        "Marks one of the adventure log entry as completed.\n\nr0: entry ID",
    )

    IsAdventureLogNotEmpty = Symbol(
        None,
        None,
        None,
        "Checks if at least one of the adventure log entry is completed.\n\nreturn:"
        " bool",
    )

    GetAdventureLogCompleted = Symbol(
        None,
        None,
        None,
        "Checks if one adventure log entry is completed.\n\nr0: entry ID\nreturn: bool",
    )

    IncrementNbDungeonsCleared = Symbol(
        None,
        None,
        None,
        "Increments by 1 the number of dungeons cleared.\n\nImplements"
        " SPECIAL_PROC_0x3A (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    GetNbDungeonsCleared = Symbol(
        None,
        None,
        None,
        "Gets the number of dungeons cleared.\n\nreturn: the number of dungeons"
        " cleared",
    )

    IncrementNbFriendRescues = Symbol(
        None,
        None,
        None,
        "Increments by 1 the number of successful friend rescues.\n\nNo params.",
    )

    GetNbFriendRescues = Symbol(
        None,
        None,
        None,
        "Gets the number of successful friend rescues.\n\nreturn: the number of"
        " successful friend rescues",
    )

    IncrementNbEvolutions = Symbol(
        None, None, None, "Increments by 1 the number of evolutions.\n\nNo params."
    )

    GetNbEvolutions = Symbol(
        None,
        None,
        None,
        "Gets the number of evolutions.\n\nreturn: the number of evolutions",
    )

    IncrementNbSteals = Symbol(
        None,
        None,
        None,
        "Leftover from Time & Darkness. Does not do anything.\n\nCalls to this matches"
        " the ones for incrementing the number of successful steals in Time &"
        " Darkness.\n\nNo params.",
    )

    IncrementNbEggsHatched = Symbol(
        None, None, None, "Increments by 1 the number of eggs hatched.\n\nNo params."
    )

    GetNbEggsHatched = Symbol(
        None,
        None,
        None,
        "Gets the number of eggs hatched.\n\nreturn: the number of eggs hatched",
    )

    GetNbPokemonJoined = Symbol(
        None,
        None,
        None,
        "Gets the number of different pokémon that joined.\n\nreturn: the number of"
        " different pokémon that joined",
    )

    GetNbMovesLearned = Symbol(
        None,
        None,
        None,
        "Gets the number of different moves learned.\n\nreturn: the number of different"
        " moves learned",
    )

    SetVictoriesOnOneFloor = Symbol(
        None,
        None,
        None,
        "Sets the record of victories on one floor.\n\nr0: the new record of victories",
    )

    GetVictoriesOnOneFloor = Symbol(
        None,
        None,
        None,
        "Gets the record of victories on one floor.\n\nreturn: the record of victories",
    )

    SetPokemonJoined = Symbol(
        None, None, None, "Marks one pokémon as joined.\n\nr0: monster ID"
    )

    SetPokemonBattled = Symbol(
        None, None, None, "Marks one pokémon as battled.\n\nr0: monster ID"
    )

    GetNbPokemonBattled = Symbol(
        None,
        None,
        None,
        "Gets the number of different pokémon that battled against you.\n\nreturn: the"
        " number of different pokémon that battled against you",
    )

    IncrementNbBigTreasureWins = Symbol(
        None,
        None,
        None,
        "Increments by 1 the number of big treasure wins.\n\nImplements"
        " SPECIAL_PROC_0x3B (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    SetNbBigTreasureWins = Symbol(
        None,
        None,
        None,
        "Sets the number of big treasure wins.\n\nr0: the new number of big treasure"
        " wins",
    )

    GetNbBigTreasureWins = Symbol(
        None,
        None,
        None,
        "Gets the number of big treasure wins.\n\nreturn: the number of big treasure"
        " wins",
    )

    SetNbRecycled = Symbol(
        None,
        None,
        None,
        "Sets the number of items recycled.\n\nr0: the new number of items recycled",
    )

    GetNbRecycled = Symbol(
        None,
        None,
        None,
        "Gets the number of items recycled.\n\nreturn: the number of items recycled",
    )

    IncrementNbSkyGiftsSent = Symbol(
        None,
        None,
        None,
        "Increments by 1 the number of sky gifts sent.\n\nImplements"
        " SPECIAL_PROC_SEND_SKY_GIFT_TO_GUILDMASTER (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    SetNbSkyGiftsSent = Symbol(
        None,
        None,
        None,
        "Sets the number of Sky Gifts sent.\n\nreturn: the number of Sky Gifts sent",
    )

    GetNbSkyGiftsSent = Symbol(
        None,
        None,
        None,
        "Gets the number of Sky Gifts sent.\n\nreturn: the number of Sky Gifts sent",
    )

    ComputeSpecialCounters = Symbol(
        None,
        None,
        None,
        "Computes the counters from the bit fields in the adventure log, as they are"
        " not updated automatically when bit fields are altered.\n\nAffects"
        " GetNbPokemonJoined, GetNbMovesLearned, GetNbPokemonBattled and"
        " GetNbItemAcquired.\n\nNo params.",
    )

    RecruitSpecialPokemonLog = Symbol(
        None,
        None,
        None,
        "Marks a specified special pokémon as recruited in the adventure log.\n\nr0:"
        " monster ID",
    )

    IncrementNbFainted = Symbol(
        None,
        None,
        None,
        "Increments by 1 the number of times you fainted.\n\nNo params.",
    )

    GetNbFainted = Symbol(
        None,
        None,
        None,
        "Gets the number of times you fainted.\n\nreturn: the number of times you"
        " fainted",
    )

    SetItemAcquired = Symbol(
        None, None, None, "Marks one specific item as acquired.\n\nr0: item ID"
    )

    GetNbItemAcquired = Symbol(
        None,
        None,
        None,
        "Gets the number of items acquired.\n\nreturn: the number of items acquired",
    )

    SetChallengeLetterCleared = Symbol(
        None, None, None, "Sets a challenge letter as cleared.\n\nr0: challenge ID"
    )

    GetSentryDutyGamePoints = Symbol(
        None,
        None,
        None,
        "Gets the points for the associated rank in the footprints minigame.\n\nr0: the"
        " rank (range 0-4, 1st to 5th)\nreturn: points",
    )

    SetSentryDutyGamePoints = Symbol(
        None,
        None,
        None,
        "Sets a new record in the footprints minigame.\n\nr0: points\nreturn: the rank"
        " (range 0-4, 1st to 5th; -1 if out of ranking)",
    )

    SubFixedPoint = Symbol(
        None,
        None,
        None,
        "Compute the subtraction of two decimal fixed-point numbers (16 fraction"
        " bits).\n\nFloats are in the format {16-bit integer part, 16-bit thousandths},"
        " where the integer part is the lower word. Probably used primarily for"
        " belly.\n\nr0: float\nr1: decrement\nreturn: max(float - decrement, 0)",
    )

    BinToDecFixedPoint = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Compute the ceiling of a decimal fixed-point number (16 fraction"
        " bits).\n\nFloats are in the format {16-bit integer part, 16-bit thousandths},"
        " where the integer part is the lower word. Probably used primarily for"
        " belly.\n\nr0: float\nreturn: ceil(float)",
    )

    DungeonGoesUp = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
        None,
        "Checks if a monster ID is an Unown.\n\nr0: monster ID\nreturn: bool",
    )

    IsShaymin = Symbol(
        None,
        None,
        None,
        "Checks if a monster ID is a Shaymin form.\n\nr0: monster ID\nreturn: bool",
    )

    IsCastform = Symbol(
        None,
        None,
        None,
        "Checks if a monster ID is a Castform form.\n\nr0: monster ID\nreturn: bool",
    )

    IsCherrim = Symbol(
        None,
        None,
        None,
        "Checks if a monster ID is a Cherrim form.\n\nr0: monster ID\nreturn: bool",
    )

    IsDeoxys = Symbol(
        None,
        None,
        None,
        "Checks if a monster ID is a Deoxys form.\n\nr0: monster ID\nreturn: bool",
    )

    IsMonsterOnTeam = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Implements SPECIAL_PROC_SET_TEAM_SETUP_HERO_AND_PARTNER_ONLY (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    SetTeamSetupHeroOnly = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_SET_TEAM_SETUP_HERO_ONLY (see"
        " ScriptSpecialProcessCall).\n\nNo params.",
    )

    GetPartyMembers = Symbol(
        None,
        None,
        None,
        "Appears to get the team's active party members. Implements most of"
        " SPECIAL_PROC_IS_TEAM_SETUP_SOLO (see ScriptSpecialProcessCall).\n\nr0:"
        " [output] Array of 4 2-byte values (they seem to be indexes of some sort)"
        " describing each party member, which will be filled in by the function. The"
        " input can be a null pointer if the party members aren't needed\nreturn:"
        " Number of party members",
    )

    IqSkillFlagTest = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Implements SPECIAL_PROC_GET_SOS_MAIL_COUNT (see"
        " ScriptSpecialProcessCall).\n\nr0: ?\nr1: some flag?\nreturn: SOS mail count",
    )

    DungeonRequestsDone = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Calls DungeonRequestsDone with the second argument set to true, and converts"
        " the integer output to a boolean.\n\nr0: ?\nreturn: bool: whether the number"
        " of missions completed is greater than 0",
    )

    ScriptSpecialProcess0x3D = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_0x3D (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x3E = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_0x3E (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ScriptSpecialProcess0x17 = Symbol(
        None,
        None,
        None,
        "Implements SPECIAL_PROC_0x17 (see ScriptSpecialProcessCall).\n\nNo params.",
    )

    ItemAtTableIdx = Symbol(
        None,
        None,
        None,
        "Gets info about the item at a given item table (not sure what this table"
        " is...) index.\n\nUsed by SPECIAL_PROC_COUNT_TABLE_ITEM_TYPE_IN_BAG and"
        " friends (see ScriptSpecialProcessCall).\n\nr0: table index\nr1: [output]"
        " pointer to an owned_item",
    )

    WaitForInterrupt = Symbol(
        None,
        None,
        None,
        "Presumably blocks until the program receives an interrupt.\n\nThis just calls"
        " (in Ghidra terminology) coproc_moveto_Wait_for_interrupt(0). See"
        " https://en.wikipedia.org/wiki/ARM_architecture_family#Coprocessors.\n\nNo"
        " params.",
    )

    FileInit = Symbol(
        None,
        None,
        None,
        "Initializes a file_stream structure for file I/O.\n\nThis function must always"
        " be called before opening a file.\n\nr0: file_stream pointer",
    )

    Abs = Symbol(
        None,
        None,
        None,
        "Takes the absolute value of an integer.\n\nr0: x\nreturn: abs(x)",
    )

    Mbtowc = Symbol(
        None,
        None,
        None,
        "The mbtowc(3) C library function.\n\nr0: pwc\nr1: s\nr2: n\nreturn: number of"
        " consumed bytes, or -1 on failure",
    )

    TryAssignByte = Symbol(
        None,
        None,
        None,
        "Assign a byte to the target of a pointer if the pointer is non-null.\n\nr0:"
        " pointer\nr1: value\nreturn: true on success, false on failure",
    )

    TryAssignByteWrapper = Symbol(
        None,
        None,
        None,
        "Wrapper around TryAssignByte.\n\nAccesses the TryAssignByte function with a"
        " weird chain of pointer dereferences.\n\nr0: pointer\nr1: value\nreturn: true"
        " on success, false on failure",
    )

    Wcstombs = Symbol(
        None,
        None,
        None,
        "The wcstombs(3) C library function.\n\nr0: dest\nr1: src\nr2: n\nreturn:"
        " characters converted",
    )

    Memcpy = Symbol(
        None,
        None,
        None,
        "The memcpy(3) C library function.\n\nr0: dest\nr1: src\nr2: n",
    )

    Memmove = Symbol(
        None,
        None,
        None,
        "The memmove(3) C library function.\n\nThe implementation is nearly the same as"
        " Memcpy, but it copies bytes from back to front if src < dst.\n\nr0: dest\nr1:"
        " src\nr2: n",
    )

    Memset = Symbol(
        None,
        None,
        None,
        "The memset(3) C library function.\n\nThis is just a wrapper around"
        " MemsetInternal that returns the pointer at the end.\n\nr0: s\nr1: c (int, but"
        " must be a single-byte value)\nr2: n\nreturn: s",
    )

    Memchr = Symbol(
        None,
        None,
        None,
        "The memchr(3) C library function.\n\nr0: s\nr1: c\nr2: n\nreturn: pointer to"
        " first occurrence of c in s, or a null pointer if no match",
    )

    Memcmp = Symbol(
        None,
        None,
        None,
        "The memcmp(3) C library function.\n\nr0: s1\nr1: s2\nr2: n\nreturn: comparison"
        " value",
    )

    MemsetInternal = Symbol(
        None,
        None,
        None,
        "The actual memory-setting implementation for the memset(3) C library"
        " function.\n\nThis function is optimized to set bytes in 4-byte chunks for n"
        " >= 32, correctly handling any unaligned bytes at the front/back. In this"
        " case, it also further optimizes by unrolling a for loop to set 8 4-byte"
        " values at once (effectively a 32-byte chunk).\n\nr0: s\nr1: c (int, but must"
        " be a single-byte value)\nr2: n",
    )

    VsprintfInternalSlice = Symbol(
        None,
        None,
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
        None,
        None,
        None,
        "Best-effort append the given data to a slice. If the slice's capacity is"
        " reached, any remaining data will be truncated.\n\nr0: slice pointer\nr1:"
        " buffer of data to append\nr2: number of bytes in the data buffer\nreturn:"
        " true",
    )

    VsprintfInternal = Symbol(
        None,
        None,
        None,
        "This is what implements Vsprintf. It's akin to __vsprintf_internal in the"
        " modern-day version of glibc (in fact, it's probably an older version of"
        " this).\n\nr0: str\nr1: maxlen (Vsprintf passes UINT32_MAX for this)\nr2:"
        " format\nr3: ap\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    Vsprintf = Symbol(
        None,
        None,
        None,
        "The vsprintf(3) C library function.\n\nr0: str\nr1: format\nr2: ap\nreturn:"
        " number of characters printed, excluding the null-terminator",
    )

    Snprintf = Symbol(
        None,
        None,
        None,
        "The snprintf(3) C library function.\n\nThis calls VsprintfInternal directly,"
        " so it's presumably the real snprintf.\n\nr0: str\nr1: n\nr2: format\n...:"
        " variadic\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    Sprintf = Symbol(
        None,
        None,
        None,
        "The sprintf(3) C library function.\n\nThis calls VsprintfInternal directly, so"
        " it's presumably the real sprintf.\n\nr0: str\nr1: format\n...:"
        " variadic\nreturn: number of characters printed, excluding the"
        " null-terminator",
    )

    Strlen = Symbol(
        None,
        None,
        None,
        "The strlen(3) C library function.\n\nr0: s\nreturn: length of s",
    )

    Strcpy = Symbol(
        None,
        None,
        None,
        "The strcpy(3) C library function.\n\nThis function is optimized to copy"
        " characters in aligned 4-byte chunks if possible, correctly handling any"
        " unaligned bytes at the front/back.\n\nr0: dest\nr1: src",
    )

    Strncpy = Symbol(
        None,
        None,
        None,
        "The strncpy(3) C library function.\n\nr0: dest\nr1: src\nr2: n",
    )

    Strcat = Symbol(
        None, None, None, "The strcat(3) C library function.\n\nr0: dest\nr1: src"
    )

    Strncat = Symbol(
        None,
        None,
        None,
        "The strncat(3) C library function.\n\nr0: dest\nr1: src\nr2: n",
    )

    Strcmp = Symbol(
        None,
        None,
        None,
        "The strcmp(3) C library function.\n\nSimilarly to Strcpy, this function is"
        " optimized to compare characters in aligned 4-byte chunks if possible.\n\nr0:"
        " s1\nr1: s2\nreturn: comparison value",
    )

    Strncmp = Symbol(
        None,
        None,
        None,
        "The strncmp(3) C library function.\n\nr0: s1\nr1: s2\nr2: n\nreturn:"
        " comparison value",
    )

    Strchr = Symbol(
        None,
        None,
        None,
        "The strchr(3) C library function.\n\nr0: string\nr1: c\nreturn: pointer to the"
        " located byte c, or null pointer if no match",
    )

    Strcspn = Symbol(
        None,
        None,
        None,
        "The strcspn(3) C library function.\n\nr0: string\nr1: stopset\nreturn: offset"
        " of the first character in string within stopset",
    )

    Strstr = Symbol(
        None,
        None,
        None,
        "The strstr(3) C library function.\n\nr0: haystack\nr1: needle\nreturn: pointer"
        " into haystack where needle starts, or null pointer if no match",
    )

    Wcslen = Symbol(
        None,
        None,
        None,
        "The wcslen(3) C library function.\n\nr0: ws\nreturn: length of ws",
    )

    AddFloat = Symbol(
        None,
        None,
        None,
        "This appears to be the libgcc implementation of __addsf3 (not sure which gcc"
        " version), which implements the addition operator for IEEE 754 floating-point"
        " numbers.\n\nr0: a\nr1: b\nreturn: a + b",
    )

    DivideFloat = Symbol(
        None,
        None,
        None,
        "This appears to be the libgcc implementation of __divsf3 (not sure which gcc"
        " version), which implements the division operator for IEEE 754 floating-point"
        " numbers.\n\nr0: dividend\nr1: divisor\nreturn: dividend / divisor",
    )

    FloatToDouble = Symbol(
        None,
        None,
        None,
        "This appears to be the libgcc implementation of __extendsfdf2 (not sure which"
        " gcc version), which implements the float to double cast operation for IEEE"
        " 754 floating-point numbers.\n\nr0: float\nreturn: (double)float",
    )

    FloatToInt = Symbol(
        None,
        None,
        None,
        "This appears to be the libgcc implementation of __fixsfsi (not sure which gcc"
        " version), which implements the float to int cast operation for IEEE 754"
        " floating-point numbers. The output saturates if the input is out of the"
        " representable range for the int type.\n\nr0: float\nreturn: (int)float",
    )

    IntToFloat = Symbol(
        None,
        None,
        None,
        "This appears to be the libgcc implementation of __floatsisf (not sure which"
        " gcc version), which implements the int to float cast operation for IEEE 754"
        " floating-point numbers.\n\nr0: int\nreturn: (float)int",
    )

    UIntToFloat = Symbol(
        None,
        None,
        None,
        "This appears to be the libgcc implementation of __floatunsisf (not sure which"
        " gcc version), which implements the unsigned int to float cast operation for"
        " IEEE 754 floating-point numbers.\n\nr0: uint\nreturn: (float)uint",
    )

    MultiplyFloat = Symbol(
        None,
        None,
        None,
        "This appears to be the libgcc implementation of __mulsf3 (not sure which gcc"
        " version), which implements the multiplication operator for IEEE 754"
        " floating-point numbers.",
    )

    Sqrtf = Symbol(
        None, None, None, "The sqrtf(3) C library function.\n\nr0: x\nreturn: sqrt(x)"
    )

    SubtractFloat = Symbol(
        None,
        None,
        None,
        "This appears to be the libgcc implementation of __subsf3 (not sure which gcc"
        " version), which implements the subtraction operator for IEEE 754"
        " floating-point numbers.\n\nr0: a\nr1: b\nreturn: a - b",
    )

    DivideInt = Symbol(
        None,
        None,
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
        None,
        None,
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
        None,
        None,
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


class NaItcmArm9Data:
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
        None,
        None,
        None,
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
        None,
        None,
        None,
        "Table of levels for the script engine, in which scenes can take place. There"
        " are a version-dependent number of 12-byte entries.\n\ntype: struct"
        " script_level[length / 12]",
    )

    ENTITIES = Symbol(
        None,
        None,
        None,
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
        None, None, None, "[Runtime]\n\ntype: struct adventure_log*"
    )

    ITEM_TABLES_PTRS_1 = Symbol(None, None, None, "")

    SMD_EVENTS_FUN_TABLE = Symbol(None, None, None, "")


class NaItcmArm9Section:
    name = "arm9"
    description = (
        "Hard-coded immediate values (literals) in instructions within the ARM 9"
        " binary."
    )
    loadaddress = 0x1FF8000
    length = 0x4000
    functions = NaItcmArm9Functions
    data = NaItcmArm9Data


class NaItcmOverlay0Functions:
    pass


class NaItcmOverlay0Data:
    TOP_MENU_MUSIC_ID = Symbol(None, None, None, "Music ID to play in the top menu.")


class NaItcmOverlay0Section:
    name = "overlay0"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 0."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay0Functions
    data = NaItcmOverlay0Data


class NaItcmOverlay10Functions:
    SprintfStatic = Symbol(
        None,
        None,
        None,
        "Statically defined copy of sprintf(3) in overlay 10. See arm9.yml for more"
        " information.\n\nr0: str\nr1: format\n...: variadic\nreturn: number of"
        " characters printed, excluding the null-terminator",
    )


class NaItcmOverlay10Data:
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


class NaItcmOverlay10Section:
    name = "overlay10"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 10."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay10Functions
    data = NaItcmOverlay10Data


class NaItcmOverlay34Functions:
    pass


class NaItcmOverlay34Data:
    UNKNOWN_MENU_CONFIRM = Symbol(None, None, None, "")

    DUNGEON_DEBUG_MENU = Symbol(None, None, None, "")


class NaItcmOverlay34Section:
    name = "overlay34"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 34."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay34Functions
    data = NaItcmOverlay34Data


class NaItcmOverlay1Functions:
    pass


class NaItcmOverlay1Data:
    CONTINUE_CHOICE = Symbol(None, None, None, "")

    SUBMENU = Symbol(None, None, None, "")

    MAIN_MENU = Symbol(None, None, None, "")

    MAIN_MENU_CONFIRM = Symbol(None, None, None, "")

    MAIN_DEBUG_MENU_1 = Symbol(None, None, None, "")

    MAIN_DEBUG_MENU_2 = Symbol(None, None, None, "")


class NaItcmOverlay1Section:
    name = "overlay1"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 1."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay1Functions
    data = NaItcmOverlay1Data


class NaItcmOverlay4Functions:
    pass


class NaItcmOverlay4Data:
    pass


class NaItcmOverlay4Section:
    name = "overlay4"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 4."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay4Functions
    data = NaItcmOverlay4Data


class NaItcmOverlay6Functions:
    pass


class NaItcmOverlay6Data:
    pass


class NaItcmOverlay6Section:
    name = "overlay6"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 6."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay6Functions
    data = NaItcmOverlay6Data


class NaItcmOverlay7Functions:
    pass


class NaItcmOverlay7Data:
    pass


class NaItcmOverlay7Section:
    name = "overlay7"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 7."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay7Functions
    data = NaItcmOverlay7Data


class NaItcmOverlay9Functions:
    pass


class NaItcmOverlay9Data:
    TOP_MENU_RETURN_MUSIC_ID = Symbol(
        None,
        None,
        None,
        "Song playing in the main menu when returning from the Sky Jukebox.",
    )


class NaItcmOverlay9Section:
    name = "overlay9"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 9."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay9Functions
    data = NaItcmOverlay9Data


class NaItcmOverlay30Functions:
    pass


class NaItcmOverlay30Data:
    pass


class NaItcmOverlay30Section:
    name = "overlay30"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 30."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay30Functions
    data = NaItcmOverlay30Data


class NaItcmOverlay31Functions:
    pass


class NaItcmOverlay31Data:
    DUNGEON_MAIN_MENU = Symbol(None, None, None, "")

    DUNGEON_SUBMENU_1 = Symbol(None, None, None, "")

    DUNGEON_SUBMENU_2 = Symbol(None, None, None, "")

    DUNGEON_SUBMENU_3 = Symbol(None, None, None, "")

    DUNGEON_SUBMENU_4 = Symbol(None, None, None, "")

    DUNGEON_SUBMENU_5 = Symbol(None, None, None, "")

    DUNGEON_SUBMENU_6 = Symbol(None, None, None, "")


class NaItcmOverlay31Section:
    name = "overlay31"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 31."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay31Functions
    data = NaItcmOverlay31Data


class NaItcmOverlay13Functions:
    pass


class NaItcmOverlay13Data:
    STARTERS_PARTNER_IDS = Symbol(None, None, None, "type: struct monster_id_16[21]")

    STARTERS_HERO_IDS = Symbol(None, None, None, "type: struct monster_id_16[32]")

    STARTERS_STRINGS = Symbol(None, None, None, "")

    QUIZ_QUESTION_STRINGS = Symbol(None, None, None, "")

    QUIZ_ANSWER_STRINGS = Symbol(None, None, None, "")

    UNKNOWN_MENU_1 = Symbol(None, None, None, "")


class NaItcmOverlay13Section:
    name = "overlay13"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 13."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay13Functions
    data = NaItcmOverlay13Data


class NaItcmOverlay14Functions:
    pass


class NaItcmOverlay14Data:
    FOOTPRINT_DEBUG_MENU = Symbol(None, None, None, "")


class NaItcmOverlay14Section:
    name = "overlay14"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 14."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay14Functions
    data = NaItcmOverlay14Data


class NaItcmOverlay15Functions:
    pass


class NaItcmOverlay15Data:
    BANK_MAIN_MENU = Symbol(None, None, None, "")


class NaItcmOverlay15Section:
    name = "overlay15"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 15."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay15Functions
    data = NaItcmOverlay15Data


class NaItcmOverlay16Functions:
    pass


class NaItcmOverlay16Data:
    EVO_MENU_CONFIRM = Symbol(None, None, None, "")

    EVO_SUBMENU = Symbol(None, None, None, "")

    EVO_MAIN_MENU = Symbol(None, None, None, "")


class NaItcmOverlay16Section:
    name = "overlay16"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 16."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay16Functions
    data = NaItcmOverlay16Data


class NaItcmOverlay18Functions:
    pass


class NaItcmOverlay18Data:
    MOVES_MENU_CONFIRM = Symbol(None, None, None, "")

    MOVES_SUBMENU_1 = Symbol(None, None, None, "")

    MOVES_SUBMENU_2 = Symbol(None, None, None, "")

    MOVES_MAIN_MENU = Symbol(None, None, None, "")

    MOVES_SUBMENU_3 = Symbol(None, None, None, "")

    MOVES_SUBMENU_4 = Symbol(None, None, None, "")

    MOVES_SUBMENU_5 = Symbol(None, None, None, "")

    MOVES_SUBMENU_6 = Symbol(None, None, None, "")

    MOVES_SUBMENU_7 = Symbol(None, None, None, "")


class NaItcmOverlay18Section:
    name = "overlay18"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 18."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay18Functions
    data = NaItcmOverlay18Data


class NaItcmOverlay21Functions:
    pass


class NaItcmOverlay21Data:
    SWAP_SHOP_MENU_CONFIRM = Symbol(None, None, None, "")

    SWAP_SHOP_SUBMENU_1 = Symbol(None, None, None, "")

    SWAP_SHOP_SUBMENU_2 = Symbol(None, None, None, "")

    SWAP_SHOP_MAIN_MENU_1 = Symbol(None, None, None, "")

    SWAP_SHOP_MAIN_MENU_2 = Symbol(None, None, None, "")

    SWAP_SHOP_SUBMENU_3 = Symbol(None, None, None, "")


class NaItcmOverlay21Section:
    name = "overlay21"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 21."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay21Functions
    data = NaItcmOverlay21Data


class NaItcmOverlay22Functions:
    pass


class NaItcmOverlay22Data:
    SHOP_MENU_CONFIRM = Symbol(None, None, None, "")

    SHOP_MAIN_MENU_1 = Symbol(None, None, None, "")

    SHOP_MAIN_MENU_2 = Symbol(None, None, None, "")

    SHOP_MAIN_MENU_3 = Symbol(None, None, None, "")


class NaItcmOverlay22Section:
    name = "overlay22"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 22."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay22Functions
    data = NaItcmOverlay22Data


class NaItcmOverlay23Functions:
    pass


class NaItcmOverlay23Data:
    STORAGE_MENU_CONFIRM = Symbol(None, None, None, "")

    STORAGE_MAIN_MENU_1 = Symbol(None, None, None, "")

    STORAGE_MAIN_MENU_2 = Symbol(None, None, None, "")

    STORAGE_MAIN_MENU_3 = Symbol(None, None, None, "")

    STORAGE_MAIN_MENU_4 = Symbol(None, None, None, "")


class NaItcmOverlay23Section:
    name = "overlay23"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 23."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay23Functions
    data = NaItcmOverlay23Data


class NaItcmOverlay24Functions:
    pass


class NaItcmOverlay24Data:
    DAYCARE_MENU_CONFIRM = Symbol(None, None, None, "")

    DAYCARE_MAIN_MENU = Symbol(None, None, None, "")


class NaItcmOverlay24Section:
    name = "overlay24"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 24."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay24Functions
    data = NaItcmOverlay24Data


class NaItcmOverlay26Functions:
    pass


class NaItcmOverlay26Data:
    pass


class NaItcmOverlay26Section:
    name = "overlay26"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 26."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay26Functions
    data = NaItcmOverlay26Data


class NaItcmOverlay27Functions:
    pass


class NaItcmOverlay27Data:
    DISCARD_ITEMS_MENU_CONFIRM = Symbol(None, None, None, "")

    DISCARD_ITEMS_SUBMENU_1 = Symbol(None, None, None, "")

    DISCARD_ITEMS_SUBMENU_2 = Symbol(None, None, None, "")

    DISCARD_ITEMS_MAIN_MENU = Symbol(None, None, None, "")


class NaItcmOverlay27Section:
    name = "overlay27"
    description = (
        "Hard-coded immediate values (literals) in instructions within overlay 27."
    )
    loadaddress = None
    length = None
    functions = NaItcmOverlay27Functions
    data = NaItcmOverlay27Data


class NaItcmOverlay32Functions:
    pass


class NaItcmOverlay32Data:
    pass


class NaItcmOverlay32Section:
    name = "overlay32"
    description = "Unused; all zeroes."
    loadaddress = None
    length = None
    functions = NaItcmOverlay32Functions
    data = NaItcmOverlay32Data


class NaItcmRamFunctions:
    pass


class NaItcmRamData:
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


class NaItcmRamSection:
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
    loadaddress = None
    length = None
    functions = NaItcmRamFunctions
    data = NaItcmRamData


class NaItcmOverlay35Functions:
    pass


class NaItcmOverlay35Data:
    pass


class NaItcmOverlay35Section:
    name = "overlay35"
    description = "Unused; all zeroes."
    loadaddress = None
    length = None
    functions = NaItcmOverlay35Functions
    data = NaItcmOverlay35Data


class NaItcmOverlay33Functions:
    pass


class NaItcmOverlay33Data:
    pass


class NaItcmOverlay33Section:
    name = "overlay33"
    description = "Unused; all zeroes."
    loadaddress = None
    length = None
    functions = NaItcmOverlay33Functions
    data = NaItcmOverlay33Data


class NaItcmSections:
    overlay20 = NaItcmOverlay20Section

    overlay3 = NaItcmOverlay3Section

    overlay8 = NaItcmOverlay8Section

    overlay5 = NaItcmOverlay5Section

    overlay17 = NaItcmOverlay17Section

    overlay19 = NaItcmOverlay19Section

    overlay12 = NaItcmOverlay12Section

    overlay2 = NaItcmOverlay2Section

    overlay28 = NaItcmOverlay28Section

    overlay29 = NaItcmOverlay29Section

    overlay11 = NaItcmOverlay11Section

    overlay25 = NaItcmOverlay25Section

    arm9 = NaItcmArm9Section

    overlay0 = NaItcmOverlay0Section

    overlay10 = NaItcmOverlay10Section

    overlay34 = NaItcmOverlay34Section

    overlay1 = NaItcmOverlay1Section

    overlay4 = NaItcmOverlay4Section

    overlay6 = NaItcmOverlay6Section

    overlay7 = NaItcmOverlay7Section

    overlay9 = NaItcmOverlay9Section

    overlay30 = NaItcmOverlay30Section

    overlay31 = NaItcmOverlay31Section

    overlay13 = NaItcmOverlay13Section

    overlay14 = NaItcmOverlay14Section

    overlay15 = NaItcmOverlay15Section

    overlay16 = NaItcmOverlay16Section

    overlay18 = NaItcmOverlay18Section

    overlay21 = NaItcmOverlay21Section

    overlay22 = NaItcmOverlay22Section

    overlay23 = NaItcmOverlay23Section

    overlay24 = NaItcmOverlay24Section

    overlay26 = NaItcmOverlay26Section

    overlay27 = NaItcmOverlay27Section

    overlay32 = NaItcmOverlay32Section

    ram = NaItcmRamSection

    overlay35 = NaItcmOverlay35Section

    overlay33 = NaItcmOverlay33Section

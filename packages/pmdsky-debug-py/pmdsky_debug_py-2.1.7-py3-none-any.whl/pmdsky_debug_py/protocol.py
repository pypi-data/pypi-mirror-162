from typing import Protocol, Optional, TypeVar, List, Generic, no_type_check
from dataclasses import dataclass

A = TypeVar("A")
B = TypeVar("B")


@dataclass
class Symbol(Generic[A, B]):
    # Either a list of at least one address or None if not defined for the region.
    addresses: A
    # Like addresses but memory-absolute
    absolute_addresses: A
    # None for most functions. Data fields should generally have a length defined.
    length: B
    description: str

    @property
    @no_type_check
    def address(self) -> int:
        """First / main address. Raises an IndexError/TypeError if no address is defined.
        """
        return self.addresses[0]

    @property
    @no_type_check
    def absolute_address(self) -> int:
        """First / main address (absolute). Raises an IndexError/TypeError if no address is defined.
        """
        return self.absolute_addresses[0]


T = TypeVar("T")
U = TypeVar("U")
L = TypeVar("L")


class SectionProtocol(Protocol[T, U, L]):
    name: str
    description: str
    loadaddress: L
    length: int
    functions: T
    data: U


class Overlay20FunctionsProtocol(Protocol):
    pass


class Overlay20DataProtocol(Protocol):
    RECYCLE_MENU_CONFIRM_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECYCLE_MENU_CONFIRM_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECYCLE_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECYCLE_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECYCLE_MAIN_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECYCLE_MAIN_MENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECYCLE_MAIN_MENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay20Protocol = SectionProtocol[
    Overlay20FunctionsProtocol,
    Overlay20DataProtocol,
    Optional[int],
]


class Overlay3FunctionsProtocol(Protocol):
    pass


class Overlay3DataProtocol(Protocol):
    pass


Overlay3Protocol = SectionProtocol[
    Overlay3FunctionsProtocol,
    Overlay3DataProtocol,
    Optional[int],
]


class Overlay8FunctionsProtocol(Protocol):
    pass


class Overlay8DataProtocol(Protocol):
    pass


Overlay8Protocol = SectionProtocol[
    Overlay8FunctionsProtocol,
    Overlay8DataProtocol,
    Optional[int],
]


class Overlay5FunctionsProtocol(Protocol):
    pass


class Overlay5DataProtocol(Protocol):
    pass


Overlay5Protocol = SectionProtocol[
    Overlay5FunctionsProtocol,
    Overlay5DataProtocol,
    Optional[int],
]


class Overlay17FunctionsProtocol(Protocol):
    pass


class Overlay17DataProtocol(Protocol):
    ASSEMBLY_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_MAIN_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_MAIN_MENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_4: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_5: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_6: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ASSEMBLY_SUBMENU_7: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay17Protocol = SectionProtocol[
    Overlay17FunctionsProtocol,
    Overlay17DataProtocol,
    Optional[int],
]


class Overlay19FunctionsProtocol(Protocol):
    pass


class Overlay19DataProtocol(Protocol):
    BAR_MENU_CONFIRM_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAR_MENU_CONFIRM_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAR_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAR_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAR_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay19Protocol = SectionProtocol[
    Overlay19FunctionsProtocol,
    Overlay19DataProtocol,
    Optional[int],
]


class Overlay12FunctionsProtocol(Protocol):
    pass


class Overlay12DataProtocol(Protocol):
    pass


Overlay12Protocol = SectionProtocol[
    Overlay12FunctionsProtocol,
    Overlay12DataProtocol,
    Optional[int],
]


class Overlay2FunctionsProtocol(Protocol):
    pass


class Overlay2DataProtocol(Protocol):
    pass


Overlay2Protocol = SectionProtocol[
    Overlay2FunctionsProtocol,
    Overlay2DataProtocol,
    Optional[int],
]


class Overlay28FunctionsProtocol(Protocol):
    pass


class Overlay28DataProtocol(Protocol):
    pass


Overlay28Protocol = SectionProtocol[
    Overlay28FunctionsProtocol,
    Overlay28DataProtocol,
    Optional[int],
]


class Overlay29FunctionsProtocol(Protocol):
    DungeonAlloc: Symbol[
        Optional[List[int]],
        None,
    ]

    GetDungeonPtrMaster: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonZInit: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonFree: Symbol[
        Optional[List[int]],
        None,
    ]

    RunDungeon: Symbol[
        Optional[List[int]],
        None,
    ]

    EntityIsValid: Symbol[
        Optional[List[int]],
        None,
    ]

    GetFloorType: Symbol[
        Optional[List[int]],
        None,
    ]

    TryForcedLoss: Symbol[
        Optional[List[int]],
        None,
    ]

    FixedRoomIsSubstituteRoom: Symbol[
        Optional[List[int]],
        None,
    ]

    StoryRestrictionsEnabled: Symbol[
        Optional[List[int]],
        None,
    ]

    FadeToBlack: Symbol[
        Optional[List[int]],
        None,
    ]

    GetTileAtEntity: Symbol[
        Optional[List[int]],
        None,
    ]

    CanTargetEntity: Symbol[
        Optional[List[int]],
        None,
    ]

    CanTargetPosition: Symbol[
        Optional[List[int]],
        None,
    ]

    SubstitutePlaceholderStringTags: Symbol[
        Optional[List[int]],
        None,
    ]

    UpdateMapSurveyorFlag: Symbol[
        Optional[List[int]],
        None,
    ]

    ItemIsActive: Symbol[
        Optional[List[int]],
        None,
    ]

    UpdateStatusIconFlags: Symbol[
        Optional[List[int]],
        None,
    ]

    IsOnMonsterSpawnList: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMonsterIdToSpawn: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMonsterLevelToSpawn: Symbol[
        Optional[List[int]],
        None,
    ]

    GetDirectionTowardsPosition: Symbol[
        Optional[List[int]],
        None,
    ]

    GetChebyshevDistance: Symbol[
        Optional[List[int]],
        None,
    ]

    IsPositionInSight: Symbol[
        Optional[List[int]],
        None,
    ]

    GetLeader: Symbol[
        Optional[List[int]],
        None,
    ]

    TickStatusTurnCounter: Symbol[
        Optional[List[int]],
        None,
    ]

    AdvanceFrame: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateDungeonRngSeed: Symbol[
        Optional[List[int]],
        None,
    ]

    GetDungeonRngPreseed: Symbol[
        Optional[List[int]],
        None,
    ]

    SetDungeonRngPreseed: Symbol[
        Optional[List[int]],
        None,
    ]

    InitDungeonRng: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRand16Bit: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRandInt: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRandRange: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRandOutcome: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcStatusDuration: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRngUnsetSecondary: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRngSetSecondary: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRngSetPrimary: Symbol[
        Optional[List[int]],
        None,
    ]

    TrySwitchPlace: Symbol[
        Optional[List[int]],
        None,
    ]

    ClearMonsterActionFields: Symbol[
        Optional[List[int]],
        None,
    ]

    SetMonsterActionFields: Symbol[
        Optional[List[int]],
        None,
    ]

    SetActionPassTurnOrWalk: Symbol[
        Optional[List[int]],
        None,
    ]

    SetActionRegularAttack: Symbol[
        Optional[List[int]],
        None,
    ]

    SetActionUseMoveAi: Symbol[
        Optional[List[int]],
        None,
    ]

    RunFractionalTurn: Symbol[
        Optional[List[int]],
        None,
    ]

    RunLeaderTurn: Symbol[
        Optional[List[int]],
        None,
    ]

    TrySpawnMonsterAndActivatePlusMinus: Symbol[
        Optional[List[int]],
        None,
    ]

    IsFloorOver: Symbol[
        Optional[List[int]],
        None,
    ]

    DecrementWindCounter: Symbol[
        Optional[List[int]],
        None,
    ]

    SetForcedLossReason: Symbol[
        Optional[List[int]],
        None,
    ]

    GetForcedLossReason: Symbol[
        Optional[List[int]],
        None,
    ]

    ResetDamageDesc: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSpriteIndex: Symbol[
        Optional[List[int]],
        None,
    ]

    JoinedAtRangeCheck2Veneer: Symbol[
        Optional[List[int]],
        None,
    ]

    FloorNumberIsEven: Symbol[
        Optional[List[int]],
        None,
    ]

    GetKecleonIdToSpawnByFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadMonsterSprite: Symbol[
        Optional[List[int]],
        None,
    ]

    EuFaintCheck: Symbol[
        Optional[List[int]],
        None,
    ]

    HandleFaint: Symbol[
        Optional[List[int]],
        None,
    ]

    UpdateAiTargetPos: Symbol[
        Optional[List[int]],
        None,
    ]

    TryActivateSlowStart: Symbol[
        Optional[List[int]],
        None,
    ]

    TryActivateArtificialWeatherAbilities: Symbol[
        Optional[List[int]],
        None,
    ]

    DefenderAbilityIsActive: Symbol[
        Optional[List[int]],
        None,
    ]

    IsMonster: Symbol[
        Optional[List[int]],
        None,
    ]

    TryActivateTruant: Symbol[
        Optional[List[int]],
        None,
    ]

    RestorePpAllMovesSetFlags: Symbol[
        Optional[List[int]],
        None,
    ]

    ShouldMonsterHeadToStairs: Symbol[
        Optional[List[int]],
        None,
    ]

    MewSpawnCheck: Symbol[
        Optional[List[int]],
        None,
    ]

    ExclusiveItemEffectIsActive: Symbol[
        Optional[List[int]],
        None,
    ]

    GetTeamMemberWithIqSkill: Symbol[
        Optional[List[int]],
        None,
    ]

    TeamMemberHasEnabledIqSkill: Symbol[
        Optional[List[int]],
        None,
    ]

    TeamLeaderIqSkillIsEnabled: Symbol[
        Optional[List[int]],
        None,
    ]

    HasLowHealth: Symbol[
        Optional[List[int]],
        None,
    ]

    IsSpecialStoryAlly: Symbol[
        Optional[List[int]],
        None,
    ]

    IsExperienceLocked: Symbol[
        Optional[List[int]],
        None,
    ]

    InitTeam: Symbol[
        Optional[List[int]],
        None,
    ]

    SpawnMonster: Symbol[
        Optional[List[int]],
        None,
    ]

    InitTeamMember: Symbol[
        Optional[List[int]],
        None,
    ]

    ExecuteMonsterAction: Symbol[
        Optional[List[int]],
        None,
    ]

    HasStatusThatPreventsActing: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcSpeedStage: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcSpeedStageWrapper: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNumberOfAttacks: Symbol[
        Optional[List[int]],
        None,
    ]

    SprintfStatic: Symbol[
        Optional[List[int]],
        None,
    ]

    IsMonsterCornered: Symbol[
        Optional[List[int]],
        None,
    ]

    CanAttackInDirection: Symbol[
        Optional[List[int]],
        None,
    ]

    CanAiMonsterMoveInDirection: Symbol[
        Optional[List[int]],
        None,
    ]

    ShouldMonsterRunAway: Symbol[
        Optional[List[int]],
        None,
    ]

    ShouldMonsterRunAwayVariation: Symbol[
        Optional[List[int]],
        None,
    ]

    NoGastroAcidStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    AbilityIsActive: Symbol[
        Optional[List[int]],
        None,
    ]

    LevitateIsActive: Symbol[
        Optional[List[int]],
        None,
    ]

    MonsterIsType: Symbol[
        Optional[List[int]],
        None,
    ]

    CanSeeInvisibleMonsters: Symbol[
        Optional[List[int]],
        None,
    ]

    HasDropeyeStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    IqSkillIsEnabled: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMoveTypeForMonster: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMovePower: Symbol[
        Optional[List[int]],
        None,
    ]

    AddExpSpecial: Symbol[
        Optional[List[int]],
        None,
    ]

    EnemyEvolution: Symbol[
        Optional[List[int]],
        None,
    ]

    EvolveMonster: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSleepAnimationId: Symbol[
        Optional[List[int]],
        None,
    ]

    DisplayActions: Symbol[
        Optional[List[int]],
        None,
    ]

    EndFrozenClassStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    EndCringeClassStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    RunMonsterAi: Symbol[
        Optional[List[int]],
        None,
    ]

    ApplyDamage: Symbol[
        Optional[List[int]],
        None,
    ]

    GetTypeMatchup: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcDamage: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcRecoilDamageFixed: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcDamageFixed: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcDamageFixedNoCategory: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcDamageFixedWrapper: Symbol[
        Optional[List[int]],
        None,
    ]

    ResetDamageCalcScratchSpace: Symbol[
        Optional[List[int]],
        None,
    ]

    TrySpawnMonsterAndTickSpawnCounter: Symbol[
        Optional[List[int]],
        None,
    ]

    AuraBowIsActive: Symbol[
        Optional[List[int]],
        None,
    ]

    ExclusiveItemOffenseBoost: Symbol[
        Optional[List[int]],
        None,
    ]

    ExclusiveItemDefenseBoost: Symbol[
        Optional[List[int]],
        None,
    ]

    TickNoSlipCap: Symbol[
        Optional[List[int]],
        None,
    ]

    TickStatusAndHealthRegen: Symbol[
        Optional[List[int]],
        None,
    ]

    InflictSleepStatusSingle: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictSleepStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictNightmareStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictNappingStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictYawningStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictSleeplessStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictPausedStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictInfatuatedStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictBurnStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictBurnStatusWholeTeam: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictPoisonedStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictBadlyPoisonedStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictFrozenStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictConstrictionStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictShadowHoldStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictIngrainStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictWrappedStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    FreeOtherWrappedMonsters: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictPetrifiedStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    LowerOffensiveStat: Symbol[
        Optional[List[int]],
        None,
    ]

    LowerDefensiveStat: Symbol[
        Optional[List[int]],
        None,
    ]

    BoostOffensiveStat: Symbol[
        Optional[List[int]],
        None,
    ]

    BoostDefensiveStat: Symbol[
        Optional[List[int]],
        None,
    ]

    ApplyOffensiveStatMultiplier: Symbol[
        Optional[List[int]],
        None,
    ]

    ApplyDefensiveStatMultiplier: Symbol[
        Optional[List[int]],
        None,
    ]

    BoostHitChanceStat: Symbol[
        Optional[List[int]],
        None,
    ]

    LowerHitChanceStat: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictCringeStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictParalysisStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    BoostSpeed: Symbol[
        Optional[List[int]],
        None,
    ]

    BoostSpeedOneStage: Symbol[
        Optional[List[int]],
        None,
    ]

    LowerSpeed: Symbol[
        Optional[List[int]],
        None,
    ]

    TrySealMove: Symbol[
        Optional[List[int]],
        None,
    ]

    BoostOrLowerSpeed: Symbol[
        Optional[List[int]],
        None,
    ]

    ResetHitChanceStat: Symbol[
        Optional[List[int]],
        None,
    ]

    TryActivateQuickFeet: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictConfusedStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictCoweringStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryIncreaseHp: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictLeechSeedStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    TryInflictDestinyBond: Symbol[
        Optional[List[int]],
        None,
    ]

    IsBlinded: Symbol[
        Optional[List[int]],
        None,
    ]

    RestoreMovePP: Symbol[
        Optional[List[int]],
        None,
    ]

    SetReflectDamageCountdownTo4: Symbol[
        Optional[List[int]],
        None,
    ]

    HasConditionalGroundImmunity: Symbol[
        Optional[List[int]],
        None,
    ]

    Conversion2IsActive: Symbol[
        Optional[List[int]],
        None,
    ]

    AiConsiderMove: Symbol[
        Optional[List[int]],
        None,
    ]

    TryAddTargetToAiTargetList: Symbol[
        Optional[List[int]],
        None,
    ]

    IsAiTargetEligible: Symbol[
        Optional[List[int]],
        None,
    ]

    IsTargetInRange: Symbol[
        Optional[List[int]],
        None,
    ]

    GetEntityMoveTargetAndRange: Symbol[
        Optional[List[int]],
        None,
    ]

    ApplyItemEffect: Symbol[
        Optional[List[int]],
        None,
    ]

    ViolentSeedBoost: Symbol[
        Optional[List[int]],
        None,
    ]

    ApplyGummiBoostsDungeonMode: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMaxPpWrapper: Symbol[
        Optional[List[int]],
        None,
    ]

    MoveIsNotPhysical: Symbol[
        Optional[List[int]],
        None,
    ]

    TryPounce: Symbol[
        Optional[List[int]],
        None,
    ]

    TryBlowAway: Symbol[
        Optional[List[int]],
        None,
    ]

    TryWarp: Symbol[
        Optional[List[int]],
        None,
    ]

    MoveHitCheck: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRandOutcomeUserTargetInteraction: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRandOutcomeUserAction: Symbol[
        Optional[List[int]],
        None,
    ]

    CanAiUseMove: Symbol[
        Optional[List[int]],
        None,
    ]

    CanMonsterUseMove: Symbol[
        Optional[List[int]],
        None,
    ]

    UpdateMovePp: Symbol[
        Optional[List[int]],
        None,
    ]

    LowerSshort: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMoveAnimationId: Symbol[
        Optional[List[int]],
        None,
    ]

    ShouldMovePlayAlternativeAnimation: Symbol[
        Optional[List[int]],
        None,
    ]

    DealDamageWithRecoil: Symbol[
        Optional[List[int]],
        None,
    ]

    ExecuteMoveEffect: Symbol[
        Optional[List[int]],
        None,
    ]

    DealDamage: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcDamageProjectile: Symbol[
        Optional[List[int]],
        None,
    ]

    CalcDamageFinal: Symbol[
        Optional[List[int]],
        None,
    ]

    StatusCheckerCheck: Symbol[
        Optional[List[int]],
        None,
    ]

    GetApparentWeather: Symbol[
        Optional[List[int]],
        None,
    ]

    TryWeatherFormChange: Symbol[
        Optional[List[int]],
        None,
    ]

    GetTile: Symbol[
        Optional[List[int]],
        None,
    ]

    GetTileSafe: Symbol[
        Optional[List[int]],
        None,
    ]

    GetStairsRoom: Symbol[
        Optional[List[int]],
        None,
    ]

    GravityIsActive: Symbol[
        Optional[List[int]],
        None,
    ]

    IsSecretBazaar: Symbol[
        Optional[List[int]],
        None,
    ]

    IsSecretRoom: Symbol[
        Optional[List[int]],
        None,
    ]

    IsSecretFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    GetDungeonGenInfoUnk0C: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMinimapData: Symbol[
        Optional[List[int]],
        None,
    ]

    SetMinimapDataE447: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMinimapDataE447: Symbol[
        Optional[List[int]],
        None,
    ]

    SetMinimapDataE448: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadFixedRoomDataVeneer: Symbol[
        Optional[List[int]],
        None,
    ]

    IsNormalFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    GetTileTerrain: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRand100: Symbol[
        Optional[List[int]],
        None,
    ]

    FlagHallwayJunctions: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateStandardFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateOuterRingFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateCrossroadsFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateLineFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateCrossFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateBeetleFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    MergeRoomsVertically: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateOuterRoomsFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    IsNotFullFloorFixedRoom: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateFixedRoom: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateOneRoomMonsterHouseFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateTwoRoomsWithMonsterHouseFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateExtraHallways: Symbol[
        Optional[List[int]],
        None,
    ]

    GetGridPositions: Symbol[
        Optional[List[int]],
        None,
    ]

    InitDungeonGrid: Symbol[
        Optional[List[int]],
        None,
    ]

    AssignRooms: Symbol[
        Optional[List[int]],
        None,
    ]

    CreateRoomsAndAnchors: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateSecondaryStructures: Symbol[
        Optional[List[int]],
        None,
    ]

    AssignGridCellConnections: Symbol[
        Optional[List[int]],
        None,
    ]

    CreateGridCellConnections: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateRoomImperfections: Symbol[
        Optional[List[int]],
        None,
    ]

    CreateHallway: Symbol[
        Optional[List[int]],
        None,
    ]

    EnsureConnectedGrid: Symbol[
        Optional[List[int]],
        None,
    ]

    SetTerrainObstacleChecked: Symbol[
        Optional[List[int]],
        None,
    ]

    FinalizeJunctions: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateKecleonShop: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateMonsterHouse: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateMazeRoom: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateMaze: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateMazeLine: Symbol[
        Optional[List[int]],
        None,
    ]

    SetSpawnFlag5: Symbol[
        Optional[List[int]],
        None,
    ]

    IsNextToHallway: Symbol[
        Optional[List[int]],
        None,
    ]

    ResolveInvalidSpawns: Symbol[
        Optional[List[int]],
        None,
    ]

    ConvertSecondaryTerrainToChasms: Symbol[
        Optional[List[int]],
        None,
    ]

    EnsureImpassableTilesAreWalls: Symbol[
        Optional[List[int]],
        None,
    ]

    InitializeTile: Symbol[
        Optional[List[int]],
        None,
    ]

    ResetFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    PosIsOutOfBounds: Symbol[
        Optional[List[int]],
        None,
    ]

    ShuffleSpawnPositions: Symbol[
        Optional[List[int]],
        None,
    ]

    SpawnNonEnemies: Symbol[
        Optional[List[int]],
        None,
    ]

    SpawnEnemies: Symbol[
        Optional[List[int]],
        None,
    ]

    SetSecondaryTerrainOnWall: Symbol[
        Optional[List[int]],
        None,
    ]

    GenerateSecondaryTerrainFormations: Symbol[
        Optional[List[int]],
        None,
    ]

    StairsAlwaysReachable: Symbol[
        Optional[List[int]],
        None,
    ]

    ConvertWallsToChasms: Symbol[
        Optional[List[int]],
        None,
    ]

    ResetInnerBoundaryTileRows: Symbol[
        Optional[List[int]],
        None,
    ]

    SpawnStairs: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadFixedRoomData: Symbol[
        Optional[List[int]],
        None,
    ]

    IsHiddenStairsFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    HasHeldItem: Symbol[
        Optional[List[int]],
        None,
    ]

    IsOutlawOrChallengeRequestFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    IsCurrentMissionType: Symbol[
        Optional[List[int]],
        None,
    ]

    IsCurrentMissionTypeExact: Symbol[
        Optional[List[int]],
        None,
    ]

    IsOutlawMonsterHouseFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    IsGoldenChamber: Symbol[
        Optional[List[int]],
        None,
    ]

    IsLegendaryChallengeFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    IsJirachiChallengeFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    IsDestinationFloorWithMonster: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadMissionMonsterSprites: Symbol[
        Optional[List[int]],
        None,
    ]

    MissionTargetEnemyIsDefeated: Symbol[
        Optional[List[int]],
        None,
    ]

    SetMissionTargetEnemyDefeated: Symbol[
        Optional[List[int]],
        None,
    ]

    IsDestinationFloorWithFixedRoom: Symbol[
        Optional[List[int]],
        None,
    ]

    GetItemToRetrieve: Symbol[
        Optional[List[int]],
        None,
    ]

    GetItemToDeliver: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSpecialTargetItem: Symbol[
        Optional[List[int]],
        None,
    ]

    IsDestinationFloorWithItem: Symbol[
        Optional[List[int]],
        None,
    ]

    IsDestinationFloorWithHiddenOutlaw: Symbol[
        Optional[List[int]],
        None,
    ]

    IsDestinationFloorWithFleeingOutlaw: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMissionTargetEnemy: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMissionEnemyMinionGroup: Symbol[
        Optional[List[int]],
        None,
    ]

    SetTargetMonsterNotFoundFlag: Symbol[
        Optional[List[int]],
        None,
    ]

    GetTargetMonsterNotFoundFlag: Symbol[
        Optional[List[int]],
        None,
    ]

    FloorHasMissionMonster: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessageByIdWithPopupCheckUser: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessageWithPopupCheckUser: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessageByIdQuiet: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessageQuiet: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessageByIdWithPopupCheckUserTarget: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessageWithPopupCheckUserTarget: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessageByIdQuietCheckUserTarget: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessageByIdWithPopupCheckUserUnknown: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessageByIdWithPopup: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessageWithPopup: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessage: Symbol[
        Optional[List[int]],
        None,
    ]

    LogMessageById: Symbol[
        Optional[List[int]],
        None,
    ]

    OpenMessageLog: Symbol[
        Optional[List[int]],
        None,
    ]

    RunDungeonMode: Symbol[
        Optional[List[int]],
        None,
    ]

    DisplayDungeonTip: Symbol[
        Optional[List[int]],
        None,
    ]

    SetBothScreensWindowColorToDefault: Symbol[
        Optional[List[int]],
        None,
    ]

    DisplayMessage: Symbol[
        Optional[List[int]],
        None,
    ]

    DisplayMessage2: Symbol[
        Optional[List[int]],
        None,
    ]

    DisplayMessageInternal: Symbol[
        Optional[List[int]],
        None,
    ]


class Overlay29DataProtocol(Protocol):
    DUNGEON_STRUCT_SIZE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAX_HP_CAP: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OFFSET_OF_DUNGEON_FLOOR_PROPERTIES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPAWN_RAND_MAX: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_PRNG_LCG_MULTIPLIER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_PRNG_LCG_INCREMENT_SECONDARY: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    KECLEON_FEMALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    KECLEON_MALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MSG_ID_SLOW_START: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXPERIENCE_POINT_GAIN_CAP: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    JUDGMENT_MOVE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    REGULAR_ATTACK_MOVE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEOXYS_ATTACK_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEOXYS_SPEED_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GIRATINA_ALTERED_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PUNISHMENT_MOVE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OFFENSE_STAT_MAX: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PROJECTILE_MOVE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BELLY_LOST_PER_TURN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVE_TARGET_AND_RANGE_SPECIAL_USER_HEALING: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PLAIN_SEED_VALUE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAX_ELIXIR_PP_RESTORATION: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SLIP_SEED_VALUE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CASTFORM_NORMAL_FORM_MALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CASTFORM_NORMAL_FORM_FEMALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CHERRIM_SUNSHINE_FORM_MALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CHERRIM_OVERCAST_FORM_FEMALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CHERRIM_SUNSHINE_FORM_FEMALE_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FLOOR_GENERATION_STATUS_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OFFSET_OF_DUNGEON_N_NORMAL_ITEM_SPAWNS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_GRID_COLUMN_BYTES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEFAULT_MAX_POSITION: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OFFSET_OF_DUNGEON_GUARANTEED_ITEM_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_TILE_SPAWN_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_REVISIT_OVERRIDES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_MONSTER_SPAWN_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_ITEM_SPAWN_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_ENTITY_SPAWN_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_MUZZLED: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_MAGNET_RISE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_MIRACLE_EYE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_LEECH_SEED: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_LONG_TOSS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_BLINDED: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_BURN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_SURE_SHOT: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_INVISIBLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_SLEEP: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_CURSE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_FREEZE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_CRINGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_BIDE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STATUS_ICON_ARRAY_REFLECT: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DIRECTIONS_XY: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FRACTIONAL_TURN_SEQUENCE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BELLY_DRAIN_IN_WALLS_INT: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BELLY_DRAIN_IN_WALLS_THOUSANDTHS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPATK_STAT_IDX: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ATK_STAT_IDX: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CORNER_CARDINAL_NEIGHBOR_IS_OPEN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_PTR_MASTER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LEADER_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_PRNG_STATE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_PRNG_STATE_SECONDARY_VALUES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCL_ITEM_EFFECTS_WEATHER_ATK_SPEED_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCL_ITEM_EFFECTS_WEATHER_MOVE_SPEED_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCL_ITEM_EFFECTS_WEATHER_NO_STATUS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCL_ITEM_EFFECTS_EVASION_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEFAULT_TILE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_DATA_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    NECTAR_IQ_BOOST: Symbol[
        Optional[List[int]],
        None,
    ]


Overlay29Protocol = SectionProtocol[
    Overlay29FunctionsProtocol,
    Overlay29DataProtocol,
    Optional[int],
]


class Overlay11FunctionsProtocol(Protocol):
    FuncThatCallsCommandParsing: Symbol[
        Optional[List[int]],
        None,
    ]

    ScriptCommandParsing: Symbol[
        Optional[List[int]],
        None,
    ]

    SsbLoad2: Symbol[
        Optional[List[int]],
        None,
    ]

    StationLoadHanger: Symbol[
        Optional[List[int]],
        None,
    ]

    ScriptStationLoadTalk: Symbol[
        Optional[List[int]],
        None,
    ]

    SsbLoad1: Symbol[
        Optional[List[int]],
        None,
    ]

    ScriptSpecialProcessCall: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSpecialRecruitmentSpecies: Symbol[
        Optional[List[int]],
        None,
    ]

    PrepareMenuAcceptTeamMember: Symbol[
        Optional[List[int]],
        None,
    ]

    InitRandomNpcJobs: Symbol[
        Optional[List[int]],
        None,
    ]

    GetRandomNpcJobType: Symbol[
        Optional[List[int]],
        None,
    ]

    GetRandomNpcJobSubtype: Symbol[
        Optional[List[int]],
        None,
    ]

    GetRandomNpcJobStillAvailable: Symbol[
        Optional[List[int]],
        None,
    ]

    AcceptRandomNpcJob: Symbol[
        Optional[List[int]],
        None,
    ]

    GroundMainLoop: Symbol[
        Optional[List[int]],
        None,
    ]

    GetAllocArenaGround: Symbol[
        Optional[List[int]],
        None,
    ]

    GetFreeArenaGround: Symbol[
        Optional[List[int]],
        None,
    ]

    GroundMainReturnDungeon: Symbol[
        Optional[List[int]],
        None,
    ]

    GroundMainNextDay: Symbol[
        Optional[List[int]],
        None,
    ]

    JumpToTitleScreen: Symbol[
        Optional[List[int]],
        None,
    ]

    ReturnToTitleScreen: Symbol[
        Optional[List[int]],
        None,
    ]

    ScriptSpecialProcess0x16: Symbol[
        Optional[List[int]],
        None,
    ]

    SprintfStatic: Symbol[
        Optional[List[int]],
        None,
    ]

    StatusUpdate: Symbol[
        Optional[List[int]],
        None,
    ]


class Overlay11DataProtocol(Protocol):
    SCRIPT_OP_CODES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    C_ROUTINES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OBJECTS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECRUITMENT_TABLE_LOCATIONS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECRUITMENT_TABLE_LEVELS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECRUITMENT_TABLE_SPECIES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LEVEL_TILEMAP_LIST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OVERLAY11_OVERLAY_LOAD_TABLE: Symbol[
        Optional[List[int]],
        None,
    ]

    UNIONALL_RAM_ADDRESS: Symbol[
        Optional[List[int]],
        None,
    ]

    GROUND_STATE_MAP: Symbol[
        Optional[List[int]],
        None,
    ]

    GROUND_STATE_PTRS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay11Protocol = SectionProtocol[
    Overlay11FunctionsProtocol,
    Overlay11DataProtocol,
    Optional[int],
]


class Overlay25FunctionsProtocol(Protocol):
    pass


class Overlay25DataProtocol(Protocol):
    APPRAISAL_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    APPRAISAL_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    APPRAISAL_SUBMENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay25Protocol = SectionProtocol[
    Overlay25FunctionsProtocol,
    Overlay25DataProtocol,
    Optional[int],
]


class Arm9FunctionsProtocol(Protocol):
    InitMemAllocTable: Symbol[
        Optional[List[int]],
        None,
    ]

    SetMemAllocatorParams: Symbol[
        Optional[List[int]],
        None,
    ]

    GetAllocArenaDefault: Symbol[
        Optional[List[int]],
        None,
    ]

    GetFreeArenaDefault: Symbol[
        Optional[List[int]],
        None,
    ]

    InitMemArena: Symbol[
        Optional[List[int]],
        None,
    ]

    MemAllocFlagsToBlockType: Symbol[
        Optional[List[int]],
        None,
    ]

    FindAvailableMemBlock: Symbol[
        Optional[List[int]],
        None,
    ]

    SplitMemBlock: Symbol[
        Optional[List[int]],
        None,
    ]

    MemAlloc: Symbol[
        Optional[List[int]],
        None,
    ]

    MemFree: Symbol[
        Optional[List[int]],
        None,
    ]

    MemArenaAlloc: Symbol[
        Optional[List[int]],
        None,
    ]

    CreateMemArena: Symbol[
        Optional[List[int]],
        None,
    ]

    MemLocateSet: Symbol[
        Optional[List[int]],
        None,
    ]

    MemLocateUnset: Symbol[
        Optional[List[int]],
        None,
    ]

    RoundUpDiv256: Symbol[
        Optional[List[int]],
        None,
    ]

    MultiplyByFixedPoint: Symbol[
        Optional[List[int]],
        None,
    ]

    UMultiplyByFixedPoint: Symbol[
        Optional[List[int]],
        None,
    ]

    GetRngSeed: Symbol[
        Optional[List[int]],
        None,
    ]

    SetRngSeed: Symbol[
        Optional[List[int]],
        None,
    ]

    Rand16Bit: Symbol[
        Optional[List[int]],
        None,
    ]

    RandInt: Symbol[
        Optional[List[int]],
        None,
    ]

    RandRange: Symbol[
        Optional[List[int]],
        None,
    ]

    Rand32Bit: Symbol[
        Optional[List[int]],
        None,
    ]

    RandIntSafe: Symbol[
        Optional[List[int]],
        None,
    ]

    RandRangeSafe: Symbol[
        Optional[List[int]],
        None,
    ]

    WaitForever: Symbol[
        Optional[List[int]],
        None,
    ]

    InitMemAllocTableVeneer: Symbol[
        Optional[List[int]],
        None,
    ]

    MemZero: Symbol[
        Optional[List[int]],
        None,
    ]

    MemcpySimple: Symbol[
        Optional[List[int]],
        None,
    ]

    TaskProcBoot: Symbol[
        Optional[List[int]],
        None,
    ]

    EnableAllInterrupts: Symbol[
        Optional[List[int]],
        None,
    ]

    GetTime: Symbol[
        Optional[List[int]],
        None,
    ]

    DisableAllInterrupts: Symbol[
        Optional[List[int]],
        None,
    ]

    SoundResume: Symbol[
        Optional[List[int]],
        None,
    ]

    CardPullOutWithStatus: Symbol[
        Optional[List[int]],
        None,
    ]

    CardPullOut: Symbol[
        Optional[List[int]],
        None,
    ]

    CardBackupError: Symbol[
        Optional[List[int]],
        None,
    ]

    HaltProcessDisp: Symbol[
        Optional[List[int]],
        None,
    ]

    OverlayIsLoaded: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadOverlay: Symbol[
        Optional[List[int]],
        None,
    ]

    UnloadOverlay: Symbol[
        Optional[List[int]],
        None,
    ]

    EuclideanNorm: Symbol[
        Optional[List[int]],
        None,
    ]

    ClampComponentAbs: Symbol[
        Optional[List[int]],
        None,
    ]

    KeyWaitInit: Symbol[
        Optional[List[int]],
        None,
    ]

    DataTransferInit: Symbol[
        Optional[List[int]],
        None,
    ]

    DataTransferStop: Symbol[
        Optional[List[int]],
        None,
    ]

    FileInitVeneer: Symbol[
        Optional[List[int]],
        None,
    ]

    FileOpen: Symbol[
        Optional[List[int]],
        None,
    ]

    FileGetSize: Symbol[
        Optional[List[int]],
        None,
    ]

    FileRead: Symbol[
        Optional[List[int]],
        None,
    ]

    FileSeek: Symbol[
        Optional[List[int]],
        None,
    ]

    FileClose: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadFileFromRom: Symbol[
        Optional[List[int]],
        None,
    ]

    GetDebugFlag1: Symbol[
        Optional[List[int]],
        None,
    ]

    SetDebugFlag1: Symbol[
        Optional[List[int]],
        None,
    ]

    AppendProgPos: Symbol[
        Optional[List[int]],
        None,
    ]

    DebugPrintTrace: Symbol[
        Optional[List[int]],
        None,
    ]

    DebugPrint0: Symbol[
        Optional[List[int]],
        None,
    ]

    GetDebugFlag2: Symbol[
        Optional[List[int]],
        None,
    ]

    SetDebugFlag2: Symbol[
        Optional[List[int]],
        None,
    ]

    DebugPrint: Symbol[
        Optional[List[int]],
        None,
    ]

    FatalError: Symbol[
        Optional[List[int]],
        None,
    ]

    OpenAllPackFiles: Symbol[
        Optional[List[int]],
        None,
    ]

    GetFileLengthInPackWithPackNb: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadFileInPackWithPackId: Symbol[
        Optional[List[int]],
        None,
    ]

    AllocAndLoadFileInPack: Symbol[
        Optional[List[int]],
        None,
    ]

    OpenPackFile: Symbol[
        Optional[List[int]],
        None,
    ]

    GetFileLengthInPack: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadFileInPack: Symbol[
        Optional[List[int]],
        None,
    ]

    IsAuraBow: Symbol[
        Optional[List[int]],
        None,
    ]

    SprintfStatic: Symbol[
        Optional[List[int]],
        None,
    ]

    SetMoneyCarried: Symbol[
        Optional[List[int]],
        None,
    ]

    IsBagFull: Symbol[
        Optional[List[int]],
        None,
    ]

    CountItemTypeInBag: Symbol[
        Optional[List[int]],
        None,
    ]

    AddItemToBag: Symbol[
        Optional[List[int]],
        None,
    ]

    ScriptSpecialProcess0x39: Symbol[
        Optional[List[int]],
        None,
    ]

    CountItemTypeInStorage: Symbol[
        Optional[List[int]],
        None,
    ]

    RemoveItemsTypeInStorage: Symbol[
        Optional[List[int]],
        None,
    ]

    AddItemToStorage: Symbol[
        Optional[List[int]],
        None,
    ]

    SetMoneyStored: Symbol[
        Optional[List[int]],
        None,
    ]

    GetExclusiveItemOffset: Symbol[
        Optional[List[int]],
        None,
    ]

    ApplyExclusiveItemStatBoosts: Symbol[
        Optional[List[int]],
        None,
    ]

    SetExclusiveItemEffect: Symbol[
        Optional[List[int]],
        None,
    ]

    ExclusiveItemEffectFlagTest: Symbol[
        Optional[List[int]],
        None,
    ]

    ApplyGummiBoostsGroundMode: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMoveTargetAndRange: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMoveType: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMoveAiWeight: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMoveBasePower: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMoveAccuracyOrAiChance: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMaxPp: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMoveCritChance: Symbol[
        Optional[List[int]],
        None,
    ]

    IsMoveRangeString19: Symbol[
        Optional[List[int]],
        None,
    ]

    IsRecoilMove: Symbol[
        Optional[List[int]],
        None,
    ]

    IsPunchMove: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMoveCategory: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadWteFromRom: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadWteFromFileDirectory: Symbol[
        Optional[List[int]],
        None,
    ]

    UnloadWte: Symbol[
        Optional[List[int]],
        None,
    ]

    HandleSir0Translation: Symbol[
        Optional[List[int]],
        None,
    ]

    HandleSir0TranslationVeneer: Symbol[
        Optional[List[int]],
        None,
    ]

    GetLanguageType: Symbol[
        Optional[List[int]],
        None,
    ]

    GetLanguage: Symbol[
        Optional[List[int]],
        None,
    ]

    PreprocessString: Symbol[
        Optional[List[int]],
        None,
    ]

    StrcpySimple: Symbol[
        Optional[List[int]],
        None,
    ]

    StrncpySimple: Symbol[
        Optional[List[int]],
        None,
    ]

    StringFromMessageId: Symbol[
        Optional[List[int]],
        None,
    ]

    SetScreenWindowsColor: Symbol[
        Optional[List[int]],
        None,
    ]

    SetBothScreensWindowsColor: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNotifyNote: Symbol[
        Optional[List[int]],
        None,
    ]

    SetNotifyNote: Symbol[
        Optional[List[int]],
        None,
    ]

    InitMainTeamAfterQuiz: Symbol[
        Optional[List[int]],
        None,
    ]

    ScriptSpecialProcess0x3: Symbol[
        Optional[List[int]],
        None,
    ]

    ScriptSpecialProcess0x4: Symbol[
        Optional[List[int]],
        None,
    ]

    NoteSaveBase: Symbol[
        Optional[List[int]],
        None,
    ]

    NoteLoadBase: Symbol[
        Optional[List[int]],
        None,
    ]

    GetGameMode: Symbol[
        Optional[List[int]],
        None,
    ]

    InitScriptVariableValues: Symbol[
        Optional[List[int]],
        None,
    ]

    InitEventFlagScriptVars: Symbol[
        Optional[List[int]],
        None,
    ]

    ZinitScriptVariable: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadScriptVariableRaw: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadScriptVariableValue: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadScriptVariableValueAtIndex: Symbol[
        Optional[List[int]],
        None,
    ]

    SaveScriptVariableValue: Symbol[
        Optional[List[int]],
        None,
    ]

    SaveScriptVariableValueAtIndex: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadScriptVariableValueSum: Symbol[
        Optional[List[int]],
        None,
    ]

    LoadScriptVariableValueBytes: Symbol[
        Optional[List[int]],
        None,
    ]

    SaveScriptVariableValueBytes: Symbol[
        Optional[List[int]],
        None,
    ]

    ScriptVariablesEqual: Symbol[
        Optional[List[int]],
        None,
    ]

    EventFlagBackup: Symbol[
        Optional[List[int]],
        None,
    ]

    DumpScriptVariableValues: Symbol[
        Optional[List[int]],
        None,
    ]

    RestoreScriptVariableValues: Symbol[
        Optional[List[int]],
        None,
    ]

    InitScenarioScriptVars: Symbol[
        Optional[List[int]],
        None,
    ]

    SetScenarioScriptVar: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSpecialEpisodeType: Symbol[
        Optional[List[int]],
        None,
    ]

    ScenarioFlagBackup: Symbol[
        Optional[List[int]],
        None,
    ]

    InitWorldMapScriptVars: Symbol[
        Optional[List[int]],
        None,
    ]

    InitDungeonListScriptVars: Symbol[
        Optional[List[int]],
        None,
    ]

    SetDungeonTipShown: Symbol[
        Optional[List[int]],
        None,
    ]

    GetDungeonTipShown: Symbol[
        Optional[List[int]],
        None,
    ]

    MonsterSpawnsEnabled: Symbol[
        Optional[List[int]],
        None,
    ]

    SetAdventureLogStructLocation: Symbol[
        Optional[List[int]],
        None,
    ]

    SetAdventureLogDungeonFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    GetAdventureLogDungeonFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    ClearAdventureLogStruct: Symbol[
        Optional[List[int]],
        None,
    ]

    SetAdventureLogCompleted: Symbol[
        Optional[List[int]],
        None,
    ]

    IsAdventureLogNotEmpty: Symbol[
        Optional[List[int]],
        None,
    ]

    GetAdventureLogCompleted: Symbol[
        Optional[List[int]],
        None,
    ]

    IncrementNbDungeonsCleared: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNbDungeonsCleared: Symbol[
        Optional[List[int]],
        None,
    ]

    IncrementNbFriendRescues: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNbFriendRescues: Symbol[
        Optional[List[int]],
        None,
    ]

    IncrementNbEvolutions: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNbEvolutions: Symbol[
        Optional[List[int]],
        None,
    ]

    IncrementNbSteals: Symbol[
        Optional[List[int]],
        None,
    ]

    IncrementNbEggsHatched: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNbEggsHatched: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNbPokemonJoined: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNbMovesLearned: Symbol[
        Optional[List[int]],
        None,
    ]

    SetVictoriesOnOneFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    GetVictoriesOnOneFloor: Symbol[
        Optional[List[int]],
        None,
    ]

    SetPokemonJoined: Symbol[
        Optional[List[int]],
        None,
    ]

    SetPokemonBattled: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNbPokemonBattled: Symbol[
        Optional[List[int]],
        None,
    ]

    IncrementNbBigTreasureWins: Symbol[
        Optional[List[int]],
        None,
    ]

    SetNbBigTreasureWins: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNbBigTreasureWins: Symbol[
        Optional[List[int]],
        None,
    ]

    SetNbRecycled: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNbRecycled: Symbol[
        Optional[List[int]],
        None,
    ]

    IncrementNbSkyGiftsSent: Symbol[
        Optional[List[int]],
        None,
    ]

    SetNbSkyGiftsSent: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNbSkyGiftsSent: Symbol[
        Optional[List[int]],
        None,
    ]

    ComputeSpecialCounters: Symbol[
        Optional[List[int]],
        None,
    ]

    RecruitSpecialPokemonLog: Symbol[
        Optional[List[int]],
        None,
    ]

    IncrementNbFainted: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNbFainted: Symbol[
        Optional[List[int]],
        None,
    ]

    SetItemAcquired: Symbol[
        Optional[List[int]],
        None,
    ]

    GetNbItemAcquired: Symbol[
        Optional[List[int]],
        None,
    ]

    SetChallengeLetterCleared: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSentryDutyGamePoints: Symbol[
        Optional[List[int]],
        None,
    ]

    SetSentryDutyGamePoints: Symbol[
        Optional[List[int]],
        None,
    ]

    SubFixedPoint: Symbol[
        Optional[List[int]],
        None,
    ]

    BinToDecFixedPoint: Symbol[
        Optional[List[int]],
        None,
    ]

    CeilFixedPoint: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonGoesUp: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMaxRescueAttempts: Symbol[
        Optional[List[int]],
        None,
    ]

    JoinedAtRangeCheck: Symbol[
        Optional[List[int]],
        None,
    ]

    JoinedAtRangeCheck2: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMonsterGender: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSpriteSize: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSpriteFileSize: Symbol[
        Optional[List[int]],
        None,
    ]

    GetCanMoveFlag: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMonsterPreEvolution: Symbol[
        Optional[List[int]],
        None,
    ]

    GetEvolutions: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMonsterIdFromSpawnEntry: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMonsterLevelFromSpawnEntry: Symbol[
        Optional[List[int]],
        None,
    ]

    GetMonsterGenderVeneer: Symbol[
        Optional[List[int]],
        None,
    ]

    IsUnown: Symbol[
        Optional[List[int]],
        None,
    ]

    IsShaymin: Symbol[
        Optional[List[int]],
        None,
    ]

    IsCastform: Symbol[
        Optional[List[int]],
        None,
    ]

    IsCherrim: Symbol[
        Optional[List[int]],
        None,
    ]

    IsDeoxys: Symbol[
        Optional[List[int]],
        None,
    ]

    IsMonsterOnTeam: Symbol[
        Optional[List[int]],
        None,
    ]

    CheckTeamMemberField8: Symbol[
        Optional[List[int]],
        None,
    ]

    GetTeamMemberData: Symbol[
        Optional[List[int]],
        None,
    ]

    SetTeamSetupHeroAndPartnerOnly: Symbol[
        Optional[List[int]],
        None,
    ]

    SetTeamSetupHeroOnly: Symbol[
        Optional[List[int]],
        None,
    ]

    GetPartyMembers: Symbol[
        Optional[List[int]],
        None,
    ]

    IqSkillFlagTest: Symbol[
        Optional[List[int]],
        None,
    ]

    GetExplorerMazeMonster: Symbol[
        Optional[List[int]],
        None,
    ]

    GetSosMailCount: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRequestsDone: Symbol[
        Optional[List[int]],
        None,
    ]

    DungeonRequestsDoneWrapper: Symbol[
        Optional[List[int]],
        None,
    ]

    AnyDungeonRequestsDone: Symbol[
        Optional[List[int]],
        None,
    ]

    ScriptSpecialProcess0x3D: Symbol[
        Optional[List[int]],
        None,
    ]

    ScriptSpecialProcess0x3E: Symbol[
        Optional[List[int]],
        None,
    ]

    ScriptSpecialProcess0x17: Symbol[
        Optional[List[int]],
        None,
    ]

    ItemAtTableIdx: Symbol[
        Optional[List[int]],
        None,
    ]

    WaitForInterrupt: Symbol[
        Optional[List[int]],
        None,
    ]

    FileInit: Symbol[
        Optional[List[int]],
        None,
    ]

    Abs: Symbol[
        Optional[List[int]],
        None,
    ]

    Mbtowc: Symbol[
        Optional[List[int]],
        None,
    ]

    TryAssignByte: Symbol[
        Optional[List[int]],
        None,
    ]

    TryAssignByteWrapper: Symbol[
        Optional[List[int]],
        None,
    ]

    Wcstombs: Symbol[
        Optional[List[int]],
        None,
    ]

    Memcpy: Symbol[
        Optional[List[int]],
        None,
    ]

    Memmove: Symbol[
        Optional[List[int]],
        None,
    ]

    Memset: Symbol[
        Optional[List[int]],
        None,
    ]

    Memchr: Symbol[
        Optional[List[int]],
        None,
    ]

    Memcmp: Symbol[
        Optional[List[int]],
        None,
    ]

    MemsetInternal: Symbol[
        Optional[List[int]],
        None,
    ]

    VsprintfInternalSlice: Symbol[
        Optional[List[int]],
        None,
    ]

    TryAppendToSlice: Symbol[
        Optional[List[int]],
        None,
    ]

    VsprintfInternal: Symbol[
        Optional[List[int]],
        None,
    ]

    Vsprintf: Symbol[
        Optional[List[int]],
        None,
    ]

    Snprintf: Symbol[
        Optional[List[int]],
        None,
    ]

    Sprintf: Symbol[
        Optional[List[int]],
        None,
    ]

    Strlen: Symbol[
        Optional[List[int]],
        None,
    ]

    Strcpy: Symbol[
        Optional[List[int]],
        None,
    ]

    Strncpy: Symbol[
        Optional[List[int]],
        None,
    ]

    Strcat: Symbol[
        Optional[List[int]],
        None,
    ]

    Strncat: Symbol[
        Optional[List[int]],
        None,
    ]

    Strcmp: Symbol[
        Optional[List[int]],
        None,
    ]

    Strncmp: Symbol[
        Optional[List[int]],
        None,
    ]

    Strchr: Symbol[
        Optional[List[int]],
        None,
    ]

    Strcspn: Symbol[
        Optional[List[int]],
        None,
    ]

    Strstr: Symbol[
        Optional[List[int]],
        None,
    ]

    Wcslen: Symbol[
        Optional[List[int]],
        None,
    ]

    AddFloat: Symbol[
        Optional[List[int]],
        None,
    ]

    DivideFloat: Symbol[
        Optional[List[int]],
        None,
    ]

    FloatToDouble: Symbol[
        Optional[List[int]],
        None,
    ]

    FloatToInt: Symbol[
        Optional[List[int]],
        None,
    ]

    IntToFloat: Symbol[
        Optional[List[int]],
        None,
    ]

    UIntToFloat: Symbol[
        Optional[List[int]],
        None,
    ]

    MultiplyFloat: Symbol[
        Optional[List[int]],
        None,
    ]

    Sqrtf: Symbol[
        Optional[List[int]],
        None,
    ]

    SubtractFloat: Symbol[
        Optional[List[int]],
        None,
    ]

    DivideInt: Symbol[
        Optional[List[int]],
        None,
    ]

    DivideUInt: Symbol[
        Optional[List[int]],
        None,
    ]

    DivideUIntNoZeroCheck: Symbol[
        Optional[List[int]],
        None,
    ]


class Arm9DataProtocol(Protocol):
    JUICE_BAR_NECTAR_IQ_GAIN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    TEXT_SPEED: Symbol[
        Optional[List[int]],
        None,
    ]

    HERO_START_LEVEL: Symbol[
        Optional[List[int]],
        None,
    ]

    PARTNER_START_LEVEL: Symbol[
        Optional[List[int]],
        None,
    ]

    DEFAULT_MEMORY_ARENA_SIZE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    AURA_BOW_ID_LAST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    NUMBER_OF_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAX_MONEY_CARRIED: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAX_MONEY_STORED: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SCRIPT_VARS_VALUES_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MONSTER_ID_LIMIT: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAX_RECRUITABLE_TEAM_MEMBERS: Symbol[
        Optional[List[int]],
        None,
    ]

    CART_REMOVED_IMG_DATA: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_STAT_BOOST_DATA: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_ATTACK_BOOSTS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_SPECIAL_ATTACK_BOOSTS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_DEFENSE_BOOSTS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_SPECIAL_DEFENSE_BOOSTS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_EFFECT_DATA: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_STAT_BOOST_DATA_INDEXES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RECOIL_MOVE_LIST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PUNCH_MOVE_LIST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SCRIPT_VARS_LOCALS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SCRIPT_VARS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_DATA_LIST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_RESTRICTIONS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPECIAL_BAND_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MUNCH_BELT_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GUMMI_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MIN_IQ_EXCLUSIVE_MOVE_USER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    WONDER_GUMMI_IQ_GAIN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    AURA_BOW_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MIN_IQ_ITEM_MASTER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEF_SCARF_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    POWER_BAND_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    WONDER_GUMMI_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ZINC_BAND_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    TACTICS_UNLOCK_LEVEL_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OUTLAW_LEVEL_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OUTLAW_MINION_LEVEL_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    IQ_SKILL_RESTRICTIONS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SECONDARY_TERRAIN_TYPES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SENTRY_MINIGAME_DATA: Symbol[
        Optional[List[int]],
        None,
    ]

    IQ_SKILLS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    IQ_GROUP_SKILLS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    IQ_GUMMI_GAIN_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GUMMI_BELLY_RESTORE_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAG_CAPACITY_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPECIAL_EPISODE_MAIN_CHARACTERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GUEST_MONSTER_DATA: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RANK_UP_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MONSTER_SPRITE_DATA: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MISSION_DUNGEON_UNLOCK_TABLE: Symbol[
        Optional[List[int]],
        None,
    ]

    EVENTS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ENTITIES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAP_MARKER_PLACEMENTS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MEMORY_ALLOCATION_ARENA_GETTERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PRNG_SEQUENCE_NUM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LOADED_OVERLAY_GROUP_0: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LOADED_OVERLAY_GROUP_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LOADED_OVERLAY_GROUP_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PACK_FILE_OPENED: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PACK_FILE_PATHS_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GAME_STATE_VALUES: Symbol[
        Optional[List[int]],
        None,
    ]

    DUNGEON_MOVE_TABLES: Symbol[
        Optional[List[int]],
        None,
    ]

    MOVE_DATA_TABLE_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LANGUAGE_INFO_DATA: Symbol[
        Optional[List[int]],
        None,
    ]

    NOTIFY_NOTE: Symbol[
        Optional[List[int]],
        None,
    ]

    DEFAULT_HERO_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEFAULT_PARTNER_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GAME_MODE: Symbol[
        Optional[List[int]],
        None,
    ]

    ADVENTURE_LOG_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ITEM_TABLES_PTRS_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SMD_EVENTS_FUN_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Arm9Protocol = SectionProtocol[
    Arm9FunctionsProtocol,
    Arm9DataProtocol,
    Optional[int],
]


class Overlay0FunctionsProtocol(Protocol):
    pass


class Overlay0DataProtocol(Protocol):
    TOP_MENU_MUSIC_ID: Symbol[
        Optional[List[int]],
        None,
    ]


Overlay0Protocol = SectionProtocol[
    Overlay0FunctionsProtocol,
    Overlay0DataProtocol,
    Optional[int],
]


class Overlay10FunctionsProtocol(Protocol):
    SprintfStatic: Symbol[
        Optional[List[int]],
        None,
    ]


class Overlay10DataProtocol(Protocol):
    FIRST_DUNGEON_WITH_MONSTER_HOUSE_TRAPS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAD_POISON_DAMAGE_COOLDOWN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PROTEIN_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPAWN_CAP_NO_MONSTER_HOUSE: Symbol[
        Optional[List[int]],
        None,
    ]

    OREN_BERRY_DAMAGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SITRUS_BERRY_HP_RESTORATION: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXP_ELITE_EXP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MONSTER_HOUSE_MAX_NON_MONSTER_SPAWNS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GOLD_THORN_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPAWN_COOLDOWN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ORAN_BERRY_FULL_HP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LIFE_SEED_HP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EXCLUSIVE_ITEM_EXP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    INTIMIDATOR_ACTIVATION_CHANCE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ORAN_BERRY_HP_RESTORATION: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SITRUS_BERRY_FULL_HP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BURN_DAMAGE_COOLDOWN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STICK_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPAWN_COOLDOWN_THIEF_ALERT: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MONSTER_HOUSE_MAX_MONSTER_SPAWNS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPEED_BOOST_TURNS: Symbol[
        Optional[List[int]],
        None,
    ]

    MIRACLE_CHEST_EXP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    WONDER_CHEST_EXP_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SPAWN_CAP_WITH_MONSTER_HOUSE: Symbol[
        Optional[List[int]],
        None,
    ]

    POISON_DAMAGE_COOLDOWN: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GEO_PEBBLE_DAMAGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GRAVELEROCK_DAMAGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RARE_FOSSIL_DAMAGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GINSENG_CHANCE_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    ZINC_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    IRON_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CALCIUM_STAT_BOOST: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CORSOLA_TWIG_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    CACNEA_SPIKE_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    GOLD_FANG_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SILVER_SPIKE_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    IRON_THORN_POWER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SLEEP_DURATION_RANGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    POWER_PITCHER_DAMAGE_MULTIPLIER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    AIR_BLADE_DAMAGE_MULTIPLIER: Symbol[
        Optional[List[int]],
        None,
    ]

    SPEED_BOOST_DURATION_RANGE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    OFFENSIVE_STAT_STAGE_MULTIPLIERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEFENSIVE_STAT_STAGE_MULTIPLIERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    RANDOM_MUSIC_ID_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MALE_ACCURACY_STAGE_MULTIPLIERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MALE_EVASION_STAGE_MULTIPLIERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FEMALE_ACCURACY_STAGE_MULTIPLIERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FEMALE_EVASION_STAGE_MULTIPLIERS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MUSIC_ID_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    TYPE_MATCHUP_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_MONSTER_SPAWN_STATS_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    TILESET_PROPERTIES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FIXED_ROOM_PROPERTIES_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVE_ANIMATION_INFO: Symbol[
        Optional[List[int]],
        None,
    ]


Overlay10Protocol = SectionProtocol[
    Overlay10FunctionsProtocol,
    Overlay10DataProtocol,
    Optional[int],
]


class Overlay34FunctionsProtocol(Protocol):
    pass


class Overlay34DataProtocol(Protocol):
    UNKNOWN_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_DEBUG_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay34Protocol = SectionProtocol[
    Overlay34FunctionsProtocol,
    Overlay34DataProtocol,
    Optional[int],
]


class Overlay1FunctionsProtocol(Protocol):
    pass


class Overlay1DataProtocol(Protocol):
    CONTINUE_CHOICE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SUBMENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAIN_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAIN_DEBUG_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MAIN_DEBUG_MENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay1Protocol = SectionProtocol[
    Overlay1FunctionsProtocol,
    Overlay1DataProtocol,
    Optional[int],
]


class Overlay4FunctionsProtocol(Protocol):
    pass


class Overlay4DataProtocol(Protocol):
    pass


Overlay4Protocol = SectionProtocol[
    Overlay4FunctionsProtocol,
    Overlay4DataProtocol,
    Optional[int],
]


class Overlay6FunctionsProtocol(Protocol):
    pass


class Overlay6DataProtocol(Protocol):
    pass


Overlay6Protocol = SectionProtocol[
    Overlay6FunctionsProtocol,
    Overlay6DataProtocol,
    Optional[int],
]


class Overlay7FunctionsProtocol(Protocol):
    pass


class Overlay7DataProtocol(Protocol):
    pass


Overlay7Protocol = SectionProtocol[
    Overlay7FunctionsProtocol,
    Overlay7DataProtocol,
    Optional[int],
]


class Overlay9FunctionsProtocol(Protocol):
    pass


class Overlay9DataProtocol(Protocol):
    TOP_MENU_RETURN_MUSIC_ID: Symbol[
        Optional[List[int]],
        None,
    ]


Overlay9Protocol = SectionProtocol[
    Overlay9FunctionsProtocol,
    Overlay9DataProtocol,
    Optional[int],
]


class Overlay30FunctionsProtocol(Protocol):
    pass


class Overlay30DataProtocol(Protocol):
    pass


Overlay30Protocol = SectionProtocol[
    Overlay30FunctionsProtocol,
    Overlay30DataProtocol,
    Optional[int],
]


class Overlay31FunctionsProtocol(Protocol):
    pass


class Overlay31DataProtocol(Protocol):
    DUNGEON_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_SUBMENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_SUBMENU_4: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_SUBMENU_5: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_SUBMENU_6: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay31Protocol = SectionProtocol[
    Overlay31FunctionsProtocol,
    Overlay31DataProtocol,
    Optional[int],
]


class Overlay13FunctionsProtocol(Protocol):
    pass


class Overlay13DataProtocol(Protocol):
    STARTERS_PARTNER_IDS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STARTERS_HERO_IDS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STARTERS_STRINGS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    QUIZ_QUESTION_STRINGS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    QUIZ_ANSWER_STRINGS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    UNKNOWN_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay13Protocol = SectionProtocol[
    Overlay13FunctionsProtocol,
    Overlay13DataProtocol,
    Optional[int],
]


class Overlay14FunctionsProtocol(Protocol):
    pass


class Overlay14DataProtocol(Protocol):
    FOOTPRINT_DEBUG_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay14Protocol = SectionProtocol[
    Overlay14FunctionsProtocol,
    Overlay14DataProtocol,
    Optional[int],
]


class Overlay15FunctionsProtocol(Protocol):
    pass


class Overlay15DataProtocol(Protocol):
    BANK_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay15Protocol = SectionProtocol[
    Overlay15FunctionsProtocol,
    Overlay15DataProtocol,
    Optional[int],
]


class Overlay16FunctionsProtocol(Protocol):
    pass


class Overlay16DataProtocol(Protocol):
    EVO_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EVO_SUBMENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    EVO_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay16Protocol = SectionProtocol[
    Overlay16FunctionsProtocol,
    Overlay16DataProtocol,
    Optional[int],
]


class Overlay18FunctionsProtocol(Protocol):
    pass


class Overlay18DataProtocol(Protocol):
    MOVES_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_4: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_5: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_6: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVES_SUBMENU_7: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay18Protocol = SectionProtocol[
    Overlay18FunctionsProtocol,
    Overlay18DataProtocol,
    Optional[int],
]


class Overlay21FunctionsProtocol(Protocol):
    pass


class Overlay21DataProtocol(Protocol):
    SWAP_SHOP_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SWAP_SHOP_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SWAP_SHOP_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SWAP_SHOP_MAIN_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SWAP_SHOP_MAIN_MENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SWAP_SHOP_SUBMENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay21Protocol = SectionProtocol[
    Overlay21FunctionsProtocol,
    Overlay21DataProtocol,
    Optional[int],
]


class Overlay22FunctionsProtocol(Protocol):
    pass


class Overlay22DataProtocol(Protocol):
    SHOP_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SHOP_MAIN_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SHOP_MAIN_MENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SHOP_MAIN_MENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay22Protocol = SectionProtocol[
    Overlay22FunctionsProtocol,
    Overlay22DataProtocol,
    Optional[int],
]


class Overlay23FunctionsProtocol(Protocol):
    pass


class Overlay23DataProtocol(Protocol):
    STORAGE_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STORAGE_MAIN_MENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STORAGE_MAIN_MENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STORAGE_MAIN_MENU_3: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STORAGE_MAIN_MENU_4: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay23Protocol = SectionProtocol[
    Overlay23FunctionsProtocol,
    Overlay23DataProtocol,
    Optional[int],
]


class Overlay24FunctionsProtocol(Protocol):
    pass


class Overlay24DataProtocol(Protocol):
    DAYCARE_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DAYCARE_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay24Protocol = SectionProtocol[
    Overlay24FunctionsProtocol,
    Overlay24DataProtocol,
    Optional[int],
]


class Overlay26FunctionsProtocol(Protocol):
    pass


class Overlay26DataProtocol(Protocol):
    pass


Overlay26Protocol = SectionProtocol[
    Overlay26FunctionsProtocol,
    Overlay26DataProtocol,
    Optional[int],
]


class Overlay27FunctionsProtocol(Protocol):
    pass


class Overlay27DataProtocol(Protocol):
    DISCARD_ITEMS_MENU_CONFIRM: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DISCARD_ITEMS_SUBMENU_1: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DISCARD_ITEMS_SUBMENU_2: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DISCARD_ITEMS_MAIN_MENU: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


Overlay27Protocol = SectionProtocol[
    Overlay27FunctionsProtocol,
    Overlay27DataProtocol,
    Optional[int],
]


class Overlay32FunctionsProtocol(Protocol):
    pass


class Overlay32DataProtocol(Protocol):
    pass


Overlay32Protocol = SectionProtocol[
    Overlay32FunctionsProtocol,
    Overlay32DataProtocol,
    Optional[int],
]


class RamFunctionsProtocol(Protocol):
    pass


class RamDataProtocol(Protocol):
    DUNGEON_COLORMAP_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DUNGEON_STRUCT: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MOVE_DATA_TABLE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FRAMES_SINCE_LAUNCH: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAG_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAG_ITEMS_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STORAGE_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    STORAGE_ITEM_QUANTITIES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    KECLEON_SHOP_ITEMS_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    KECLEON_SHOP_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    UNUSED_KECLEON_SHOP_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    KECLEON_WARES_ITEMS_PTR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    KECLEON_WARES_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    UNUSED_KECLEON_WARES_ITEMS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MONEY_CARRIED: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    MONEY_STORED: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LAST_NEW_MOVE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    SCRIPT_VARS_VALUES: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    BAG_LEVEL: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    DEBUG_SPECIAL_EPISODE_NUMBER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PENDING_DUNGEON_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PENDING_STARTING_FLOOR: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PLAY_TIME_SECONDS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PLAY_TIME_FRAME_COUNTER: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    TEAM_NAME: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    HERO_SPECIES_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    HERO_NICKNAME: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PARTNER_SPECIES_ID: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LEADER_IQ_SKILLS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    LEADER_NICKNAME: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    PARTY_MEMBER_2_IQ_SKILLS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FRAMES_SINCE_LAUNCH_TIMES_THREE: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    TURNING_ON_THE_SPOT_FLAG: Symbol[
        Optional[List[int]],
        Optional[int],
    ]

    FLOOR_GENERATION_STATUS: Symbol[
        Optional[List[int]],
        Optional[int],
    ]


RamProtocol = SectionProtocol[
    RamFunctionsProtocol,
    RamDataProtocol,
    Optional[int],
]


class Overlay35FunctionsProtocol(Protocol):
    pass


class Overlay35DataProtocol(Protocol):
    pass


Overlay35Protocol = SectionProtocol[
    Overlay35FunctionsProtocol,
    Overlay35DataProtocol,
    Optional[int],
]


class Overlay33FunctionsProtocol(Protocol):
    pass


class Overlay33DataProtocol(Protocol):
    pass


Overlay33Protocol = SectionProtocol[
    Overlay33FunctionsProtocol,
    Overlay33DataProtocol,
    Optional[int],
]


class AllSymbolsProtocol(Protocol):
    overlay20: Overlay20Protocol

    overlay3: Overlay3Protocol

    overlay8: Overlay8Protocol

    overlay5: Overlay5Protocol

    overlay17: Overlay17Protocol

    overlay19: Overlay19Protocol

    overlay12: Overlay12Protocol

    overlay2: Overlay2Protocol

    overlay28: Overlay28Protocol

    overlay29: Overlay29Protocol

    overlay11: Overlay11Protocol

    overlay25: Overlay25Protocol

    arm9: Arm9Protocol

    overlay0: Overlay0Protocol

    overlay10: Overlay10Protocol

    overlay34: Overlay34Protocol

    overlay1: Overlay1Protocol

    overlay4: Overlay4Protocol

    overlay6: Overlay6Protocol

    overlay7: Overlay7Protocol

    overlay9: Overlay9Protocol

    overlay30: Overlay30Protocol

    overlay31: Overlay31Protocol

    overlay13: Overlay13Protocol

    overlay14: Overlay14Protocol

    overlay15: Overlay15Protocol

    overlay16: Overlay16Protocol

    overlay18: Overlay18Protocol

    overlay21: Overlay21Protocol

    overlay22: Overlay22Protocol

    overlay23: Overlay23Protocol

    overlay24: Overlay24Protocol

    overlay26: Overlay26Protocol

    overlay27: Overlay27Protocol

    overlay32: Overlay32Protocol

    ram: RamProtocol

    overlay35: Overlay35Protocol

    overlay33: Overlay33Protocol

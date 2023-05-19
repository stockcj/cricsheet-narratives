from dataclasses import dataclass
from typing import List, Dict, Union, Optional

@dataclass
class MatchMeta:
    data_version: str
    created: str
    revision: int

@dataclass
class BowlOutDelivery:
    bowler: str
    outcome: str

@dataclass
class MatchInfoBowlOut:
    deliveries: List[BowlOutDelivery]

@dataclass
class MatchInfoEvent:
    name: str
    match_number: Optional[int] = None
    group: Optional[str] = None
    stage: Optional[str] = None

@dataclass
class MatchInfoOfficials:
    match_referees: Optional[List[str]] = None
    reserve_umpires: Optional[List[str]] = None
    tv_umpires: Optional[List[str]] = None
    umpires: Optional[List[str]] = None

@dataclass
class MatchInfoOutcome:
    by: Optional[Dict[str, int]] = None
    bowl_out: Optional[str] = None
    eliminator: Optional[str] = None
    method: Optional[str] = None
    result: Optional[str] = None
    winner: Optional[str] = None

@dataclass
class MatchInfoToss:
    decision: str
    winner: str
    uncontested: Optional[str] = None

@dataclass
class MatchInfo:
    balls_per_over: int
    dates: List[str]
    gender: str
    match_type: str
    players: Dict[str, List[str]]
    registry: Dict[str, Dict[str, str]]
    season: str
    supersubs: Dict[str, str]
    team_type: str
    outcome: MatchInfoOutcome
    teams: List[str]
    toss: MatchInfoToss
    bowl_out: Optional[MatchInfoBowlOut] = None
    city: Optional[str] = None
    event: Optional[MatchInfoEvent] = None
    match_type_number: Optional[int] = None
    missing: Optional[List[Union[str, dict]]] = None
    officials: Optional[MatchInfoOfficials] = None
    overs: Optional[int] = None
    player_of_match: Optional[List[str]] = None
    venue: Optional[str] = None

@dataclass
class MatchInningsOverDeliveryRuns:
    batter: int
    extras: int
    total: int
    non_boundary: Optional[bool] = None

@dataclass
class MatchInningsOverDelivery:
    batter: str
    bowler: str
    extras: Dict[str, int]
    non_striker: str
    runs: MatchInningsOverDeliveryRuns
    replacements: Optional[Dict] = None
    review: Optional[Dict] = None
    wickets: Optional[List[Dict[str, str]]] = None

@dataclass
class MatchInningsOver:
    over: int
    deliveries: List[MatchInningsOverDelivery]

@dataclass
class MatchInningsPowerPlay:
    first_delivery: int
    to: int
    type: int

@dataclass
class MatchInnings:
    team: str
    target: Dict[str, int]
    super_over: bool
    overs: Optional[List[MatchInningsOver]] = None
    absent_hurt: Optional[List[str]] = None
    penalty_runs: Optional[Dict[str, int]] = None
    declared: Optional[bool] = None
    forfeited: Optional[bool] = None
    powerplays: Optional[List[MatchInningsPowerPlay]] = None
    miscounted_overs: Optional[Dict] = None

@dataclass
class MatchData:
    meta: MatchMeta
    info: MatchInfo
    innings: List[MatchInnings]
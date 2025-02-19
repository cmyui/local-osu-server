import os
import time
import calendar
from ext import glob
from typing import Any
from typing import Union
import glob as builtin_glob
from typing import Optional
from datetime import datetime
from objects.replay import Replay
from objects.beatmap import Beatmap
from objects.modifiedbeatmap import ModifiedBeatmap

class BanchoScore:
    def __init__(self, bancho_score: dict[str, str]) -> None:
        self.score_id = bancho_score['score_id']
        self.username = bancho_score['username']
        self.score = bancho_score['score']
        self.maxcombo = bancho_score['maxcombo']
        self.count50 = bancho_score['count50']
        self.count100 = bancho_score['count100']
        self.count300 = bancho_score['count300']
        self.countmiss = bancho_score['countmiss']
        self.countkatu = bancho_score['countkatu']
        self.countgeki = bancho_score['countgeki']
        self.perfect = bancho_score['perfect']
        self.enabled_mods = bancho_score['enabled_mods']
        self.user_id = bancho_score['user_id']
        self.time = calendar.timegm(
            datetime.strptime(bancho_score['date'], "%Y-%m-%d %H:%M:%S").utctimetuple()
        )
        self.replay_available = bancho_score['replay_available']

    @property
    def as_leaderboard_score(self) -> dict:
        return self.__dict__.copy()

class Score:
    def __init__(
        self, mode: str, 
        md5: str, name: str,
        n300: int,  n100: int,
        n50: int, ngeki: int,
        nkatu: int, nmiss: int,
        score: int, max_combo: int,
        perfect: bool, mods: int, time: int,
        replay: Optional[Replay] = None, 
        additional_mods: Optional[int] = None,
        bmap: Optional[Union[Beatmap, ModifiedBeatmap]] = None,
        acc: Optional[float] = None, pp: Optional[float] = None, 
        replay_md5: Optional[str] = None
    ) -> None:
        self.mode = mode
        self.md5 = md5
        self.name = name
        self.n300 = n300
        self.n100 = n100
        self.n50 = n50
        self.ngeki = ngeki
        self.nkatu = nkatu
        self.nmiss = nmiss
        self.score = score
        self.max_combo = max_combo
        self.perfect = perfect
        self.mods = mods
        self.additional_mods = additional_mods
        self.replay = replay
        self.bmap = bmap
        self.acc = acc
        self.pp = pp
        self.replay_md5 = replay_md5
        self.time = time
    
    def as_dict(self) -> dict[str, Any]:
        score = self.__dict__.copy()
        score['replay_md5'] = self.replay.replay_md5 # type: ignore
        del score['replay']
        del score['bmap']
        return score

    @property
    def is_failed(self) -> bool:
        if self.mods & 1: # if user has nf
            return False

        for lifebar in self.replay.bar_graph: # type: ignore
            if lifebar.current_hp == 0.0:
                return True
        
        return False

    @classmethod
    def from_dict(cls, dictionary: dict) -> 'Score':
        if 'time' not in dictionary:
            dictionary['time'] = time.time()
        
        return Score(**dictionary)

    @classmethod
    def from_score_sub(cls) -> Optional['Score']:
        if (
            not glob.player or
            not glob.replay_folder
        ):
            return
        
        files = builtin_glob.iglob(
            str(glob.replay_folder / '*.osr')
        )

        replay_path = glob.replay_folder / max(files , key=os.path.getctime)
        replay = Replay.from_file(str(replay_path))
        
        s = cls(
            glob.player.mode, replay.beatmap_md5, replay.player_name, # type: ignore
            replay.n300, replay.n100, replay.n50, replay.geki, # type: ignore
            replay.katu, replay.miss, replay.total_score, # type: ignore
            replay.combo, bool(replay.perfect), int(replay.mods), # type: ignore
            int(time.time()), replay, int(replay.additional_mods or 0),
            replay_md5 = replay.replay_md5 # type: ignore
        )

        return s

    @property
    def as_leaderboard_score(self) -> dict:
        return {
            'score_id': 0,
            'username': self.name,
            'score': self.score,
            'maxcombo': self.max_combo,
            'count50': self.n50,
            'count100': self.n100,
            'count300': self.n300,
            'countmiss': self.nmiss,
            'countkatu': self.nkatu,
            'countgeki': self.ngeki,
            'perfect': int(self.perfect),
            'enabled_mods': self.mods,
            'user_id': 2,
            'time': self.time,
            'replay_available': 1
        }
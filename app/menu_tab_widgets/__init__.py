from .downloaded.downloaded_tab import DownloadedTab
from .playlists.playlists_tab import PlaylistsTab
from .develop.develop_tab import DevelopTab
from .statistics.statistics_tab import StatisticsTab

TAB_CLASS_MAP = {
    "Downloaded": DownloadedTab,
    "Playlists": PlaylistsTab,
    "Develop": DevelopTab,
    "Statistics": StatisticsTab
}

# Playlist2Podcast

Playlist2Podcast is a command line tool that takes a Youtube playlist and creates a podcast feed from this.

Playlist2Podcast:
1) downloads and converts the videos in one or more playlists to opus audio only files,
2) downloads thumbnails and converts them to JPEG format, and
3) creates a podcast feed with the downloaded videos and thumbnails.

Easiest way to use Playlist2Podcast is to use `pipx` to install it from PyPi. Then you can simply use
`playlist2podcast` on the command line run it.

Playlist2Podcast will ask for all necessary parameters when run for the first time and store them in `config.json`
file in the current directory.

Playlist2Podcast is licences under
the [GNU Affero General Public License v3.0](http://www.gnu.org/licenses/agpl-3.0.html)

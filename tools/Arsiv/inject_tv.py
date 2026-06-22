import codecs

tv_html = 'C:/Users/bilal/SARACAPP/templates/tv.html'
with codecs.open(tv_html, 'r', 'utf-8') as f:
    text = f.read()

# Replace ytContainer CSS with spotifyContainer CSS
css_old = """        #ytContainer {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 320px;
            height: 180px;
            background: #000;
            border-radius: 10px;
            overflow: hidden;
            border: 2px solid red;
            box-shadow: 0 0 20px rgba(255,0,0,0.3);
            display: none;
            z-index: 1000;
        }
        #ytContainer iframe {
            width: 100%;
            height: 100%;
            border: none;
        }"""

css_new = """        #spotifyContainer {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            height: 100px;
            background: #181818;
            border-radius: 12px;
            display: flex;
            align-items: center;
            padding: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            border: 1px solid #282828;
            z-index: 1000;
        }
        #spotifyContainer img {
            width: 80px;
            height: 80px;
            border-radius: 8px;
            margin-right: 15px;
            object-fit: cover;
            background: #282828;
        }
        .sp-info {
            display: flex;
            flex-direction: column;
            overflow: hidden;
            flex: 1;
        }
        #spTitle {
            color: #fff;
            font-size: 18px;
            font-weight: bold;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 5px;
        }
        #spArtist {
            color: #b3b3b3;
            font-size: 14px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }"""

text = text.replace(css_old, css_new)

# Replace ytContainer HTML with spotifyContainer and Overlay
html_old = """    <div id="ytContainer">
        <iframe id="ytIframe" src="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" allowfullscreen></iframe>
    </div>"""

html_new = """    <div id="startAudioOverlay" style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999; display:flex; justify-content:center; align-items:center; cursor:pointer;" onclick="this.style.display='none';">
        <div style="background:#1DB954; color:white; padding:20px 40px; border-radius:30px; font-size:24px; font-weight:bold; box-shadow: 0 4px 15px rgba(29,185,84,0.4);">
            ▶️ Müzik İçin Ekrana Tıklayın
        </div>
    </div>

    <div id="spotifyContainer">
        <img id="spCover" src="" />
        <div class="sp-info">
            <div id="spTitle">Spotify Bekleniyor...</div>
            <div id="spArtist">Telefonunuzdan SARACOGLU Mutfak'i secin</div>
        </div>
    </div>"""

text = text.replace(html_old, html_new)

# Replace JS logic
import re
js_pattern = re.compile(r'let currentYtLink = "";.*?} catch\(e\) \{\s*console\.error\("Ayar cekilemedi", e\);\s*\}\s*\}', re.DOTALL)

js_new = """let currentSpotifyToken = "";
        let playerReady = false;
        let spotifyPlayer = null;

        window.onSpotifyWebPlaybackSDKReady = () => {
            playerReady = true;
            initSpotifyPlayer();
        };

        function initSpotifyPlayer() {
            if (!playerReady || !currentSpotifyToken || spotifyPlayer) return;

            spotifyPlayer = new Spotify.Player({
                name: 'SARACOGLU Mutfak',
                getOAuthToken: cb => { cb(currentSpotifyToken); },
                volume: 0.5
            });

            spotifyPlayer.addListener('ready', ({ device_id }) => {
                console.log('Ready with Device ID', device_id);
                document.getElementById("spTitle").innerText = "Baglandi!";
                document.getElementById("spArtist").innerText = "Muzik acabilirsiniz";
            });

            spotifyPlayer.addListener('not_ready', ({ device_id }) => {
                console.log('Device ID has gone offline', device_id);
            });

            spotifyPlayer.addListener('player_state_changed', state => {
                if (!state) return;
                const track = state.track_window.current_track;
                if (track) {
                    document.getElementById("spTitle").innerText = track.name;
                    document.getElementById("spArtist").innerText = track.artists.map(a => a.name).join(", ");
                    if (track.album && track.album.images && track.album.images.length > 0) {
                        document.getElementById("spCover").src = track.album.images[0].url;
                    }
                }
            });

            spotifyPlayer.connect();
        }

        async function checkTvSettings() {
            try {
                const res = await fetch('/spotify/token');
                if (res.status === 200) {
                    const data = await res.json();
                    if (data.access_token && data.access_token !== currentSpotifyToken) {
                        currentSpotifyToken = data.access_token;
                        if (!document.getElementById("spotify-sdk")) {
                            const script = document.createElement("script");
                            script.id = "spotify-sdk";
                            script.src = "https://sdk.scdn.co/spotify-player.js";
                            document.body.appendChild(script);
                        } else if (playerReady && !spotifyPlayer) {
                            initSpotifyPlayer();
                        }
                    }
                }
            } catch(e) {
                console.error("Token alinamadi", e);
            }
        }"""

text = js_pattern.sub(js_new, text)

with codecs.open(tv_html, 'w', 'utf-8') as f:
    f.write(text)

print("tv.html updated for Spotify SDK.")

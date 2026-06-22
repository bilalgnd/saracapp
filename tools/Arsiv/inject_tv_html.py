import codecs

tv_html = 'C:/Users/bilal/SARACAPP/templates/tv.html'
with codecs.open(tv_html, 'r', 'utf-8') as f:
    text = f.read()

# Add YouTube Container
yt_css = """
        .empty-state h2 {
            font-size: 48px;
            margin: 0;
            opacity: 0.5;
        }

        #ytContainer {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 320px;
            height: 180px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.8);
            border: 2px solid #FF0000;
            display: none;
            z-index: 1000;
        }
        #ytContainer iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
"""
text = text.replace("""        .empty-state h2 {
            font-size: 48px;
            margin: 0;
            opacity: 0.5;
        }""", yt_css)


yt_html = """    <div class="empty-state" id="emptyState">
        <h2>Sipariş Bekleniyor...</h2>
    </div>

    <div id="ytContainer">
        <iframe id="ytIframe" src="" allow="autoplay; encrypted-media" allowfullscreen></iframe>
    </div>"""
text = text.replace("""    <div class="empty-state" id="emptyState">
        <h2>Sipariş Bekleniyor...</h2>
    </div>""", yt_html)


yt_js = """        connectWebSocket();

        let currentYtLink = "";

        function getYouTubeEmbedUrl(url) {
            if (!url) return "";
            let embedUrl = "";
            if (url.includes("playlist?list=")) {
                const listId = url.split("list=")[1].split("&")[0];
                embedUrl = `https://www.youtube.com/embed/videoseries?list=${listId}&autoplay=1`;
            } else if (url.includes("watch?v=")) {
                const videoId = url.split("v=")[1].split("&")[0];
                embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
            } else if (url.includes("youtu.be/")) {
                const videoId = url.split("youtu.be/")[1].split("?")[0];
                embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
            }
            return embedUrl;
        }

        async function checkTvSettings() {
            try {
                const res = await fetch('/tv_settings');
                const data = await res.json();
                const ytLink = data.youtube_url || "";
                
                if (ytLink !== currentYtLink) {
                    currentYtLink = ytLink;
                    const iframe = document.getElementById('ytIframe');
                    const container = document.getElementById('ytContainer');
                    
                    if (ytLink) {
                        const embedUrl = getYouTubeEmbedUrl(ytLink);
                        if (embedUrl) {
                            iframe.src = embedUrl;
                            container.style.display = 'block';
                        } else {
                            iframe.src = "";
                            container.style.display = 'none';
                        }
                    } else {
                        iframe.src = "";
                        container.style.display = 'none';
                    }
                }
            } catch(e) {
                console.error("Ayar cekilemedi", e);
            }
        }

        setInterval(checkTvSettings, 5000);
        checkTvSettings();
"""
text = text.replace("        connectWebSocket();", yt_js)

with codecs.open(tv_html, 'w', 'utf-8') as f:
    f.write(text)

print("Injected YouTube player to tv.html")


import os
import json

# Consolidated sites from all sources
all_source_sites = {
    "Streaming & Video Tubes": [
        "HQPorner", "SexyPorn", "WatchPorn.to", "Porninja", "iXXX", "PornHoarder", "Noodlemagazine", 
        "EPorner", "xHamster", "XVideos", "PornMD", "PlayHDPorn", "SpankBang", "neporn", 
        "FreePornVideos", "StreamPorn", "PornHub", "TNAFlix", "MrJerk", "ShyFap", "Youporn", 
        "PornTrex", "CUMS", "josporn", "SomePorn", "Xozilla", "5MoviesPorn", "TopVid", 
        "OK.XXX", "Hotmovix", "Youjizz", "iPornTV", "PornoBae", "Jizzbunker", "10HitMovies", 
        "pornken", "Heavy-R", "EroticMovies", "XNXX", "ThePornArea", "DrTuber", "Porndish", 
        "Analdin", "SUJ", "Tube8", "xMegaDrive", "Porndoe", "Intporn", "Siska", "Porndig", 
        "xxdbx", "anysex.com", "Kojka", "Sex-Empire", "ifuqyou", "PornXpert", "Ask4Porn", 
        "PornHD3x", "Motherless", "ClipHunter", "SexVid", "OnlinePornHub", "Beeg", "Redtube", 
        "SuperPorn", "xGoMovies", "txxx", "PORNEKIP", "Vid123",
        "PornTube", "Thumbzilla", "SunPorno", "Empflix", "Upornia", "24Porn", "Sexu", "Tiava", 
        "Fuq.com", "Alohatube", "Iwank.tv", "Vporn", "4tube", "Pornorama", "Porzo", "Oopsmovs", 
        "Flyflv", "WankSpider", "YepTube", "WinPorn", "XBabe", "Yuvutu", "Spankandbang", 
        "HotMovs", "FapVid", "AnyXXX", "BravoTube", "Redwap", "BigVideo", "4KSex", "WorldSex", 
        "PornOne", "LegalPorno", "TXXX", "Vxxx", "Fuqqt", "WankMap", "ModPorn", "Porn2All", 
        "01Tube", "HD Pussy XXX", "WardDogs", "HDzog", "PornMate", "Porn Top", "PornBox", 
        "FreePorn8", "PornWorld", "Relax Sex", "PornX", "HornyHub", "Porn HD", "HD Porn Max", 
        "HDFreePorn", "Babes34", "ManySex", "RunPorn.com",
        "Spicymature.com", "Hdzog.com", "Bigboobsxxx.com", "Tubegalore.com", "Fapvid.com", 
        "Pornyork.com", "Tubent.com", "Milf77.com", "Dinotube.com", "Tonicmovies.com", 
        "Lobstertube.com", "Ooo-sex.com", "Zzztube.com", "Rulertube.com", "4porn.com", 
        "Matureporn.com", "Tubepleasure.com", "Anysex.com", "Gayporn.com", "Bigboobs.xxx", 
        "Ebonyporn.xxx", "Lesb8.com", "Porno7.xxx", "Hellporno.com", "Vivagals.com", 
        "Tubexclips.com", "Nailedhard.com", "Maturezilla.com", "Spicytranny.com", 
        "Tubezaur.com", "Bestandfree.com", "Ice-gay.com"
    ],
    "Adult Movies / Grindhouse": [
        "Film1k", "EroticMV", "RareLust", "PandaMovies", "TubePornClassic", "MangoPorn", 
        "EroGarga", "EroticAge", "Film-Adult", "Cat3Film", "paradisehill", "Sex Film", 
        "Cat3Movies", "pornxtheatre", "AdultLoad", "WIPFilms", "VintageClassix", 
        "chuyenphim18", "Pinkueiga"
    ],
    "Asian / JAV": [
        "SexTB", "SupJav", "JAVSeen", "JAVGG", "JavGuru", "Javtiful", "missav", "JavHDPorn", 
        "nJAV", "HighPorn", "KRX18", "Senzuri Tube", "JavFan", "rou.video", "AsianGirl", 
        "javdoe", "playav", "dnaav", "JAVMost", "avjoy", "WatchFreeJAV", "91Porna", "91rb", 
        "JavFun", "JavBangers", "JavEnglish", "7MMTV", "TopDrama", "Jav-angel", 
        "KoreanPornMovies", "cosplay.jav", "JAVLibrary",
        "JavHD", "JapanHDV", "VJav", "JAVQuick", "FbJav", "TokyoTeenies", "ProjectJAV", 
        "iJAVTorrents", "PussyAV", "R18", "HCJav", "Wierd Japan", "Javlust", "Sex Jav", 
        "JAV/Asian Tube", "Tomodachinpo.com", "MalayPorner", "18av", "Asian Porn Videos", 
        "AV Jiali", "Tenshigao", "JAV Wine", "Little Asians", "Erito Network", "Xjav", "JavBraze"
    ],
    "Hentai Anime": [
        "Oppai.Stream", "hstream.moe", "Hanime.tv", "HentaiWorld", "Ohentai", "Hentai.tv", 
        "HentaiFox.tv", "AnimeIDHentai", "HentaiMama", "Hentai Moon", "HentaiPlay", 
        "HentaiCity", "HentaiSea", "AniPorn", "Hentaini", "MioHentai", "HentaiStream", 
        "Uncensored Hentai", "Hentai Haven", "HentaiFreak", "Haho", "HentaiYes", 
        "hentaigasm", "HentaiVideos.net", "UnderHentai", "HentaiPRN", "XAnimePorn", 
        "HentaiTube.online", "MuchoHentai", "HentaiCloud", "HentaisTube", "Watch Hentai", 
        "HAnime", "e-Hentai / ExHentai", "LatestHentai", "CartoonPornVideos", "Hentai2w",
        "SimplyHentai", "HentaiFox", "ManyToon", "Hentai20", "Pururin", "R34Anim", 
        "HentaiPulse", "AnimeStigma", "Fakku", "Hentaied", "HentaiStreamTv", "Hentai0", 
        "AvBebe", "HentaiDude", "HentaiZilla", "Hentai Pros", "HentaiKey", "HeyHentai", 
        "Hentai Freak", "NHentai", "Hentaistream", "HentaiFromHell", "3DPornDude", 
        "Hentai Sex School", "Ani Porn", "Hentai Fucking", "VerComicsPorno", 
        "Quadrinhos Eróticos", "Porn Hentai", "RedHentai", "Xhentai", "Ver Hentai", 
        "Hentai Guru", "8muses", "Nhentai Manga", "Hentaivideoworld", "3dhentaivideo",
        "ManhwaHentai", "MangaHentai", "Manhwax", "Manhwa68", "HentaiWebtoon", "Manhwa18", 
        "FreeComicOnline"
    ],
    "Cam Models": [
        "Archivebate", "CamCaps", "Peachurbate", "Curbate", "eCamRips", "Recurbate", 
        "Chaturflix", "VVebMGirls", "WebLove", "Camwhores Bay", "Bestcam", "LiveCamRips", 
        "OnScreens", "ShowCamRips", "Cloudbate", "Webpussi", "CamSeek.TV", "camsho.ws", 
        "WebcamRips", "StripHub", "CumCams", "CamSmut", "SexKbj / sexbjcam"
    ],
    "Leak Sites": [
        "Hotleak", "Kemono", "Coomer", "SimpCity / SimpTown", "BetterMegaPacks", "OSosedki", 
        "EroThots", "Vixenleaks", "Faponic", "Bunkr", "TurboVid", "Nudostar", "EvilX", 
        "NobodyHome", "Fapello", "OnlyFans421", "xxxTube / xxxVideo", "ThotHub"
    ]
}

with open("current_sites.txt", "r") as f:
    current_sites = [line.strip().lower() for line in f.readlines()]

def normalize(name):
    return name.lower().replace(" ", "").replace(".com", "").replace(".to", "").replace(".tv", "").replace(".net", "").replace(".xxx", "").replace("-", "").replace("/", "")

current_normalized = [normalize(s) for s in current_sites]

results = []
seen_normalized = set()

for category, sites in all_source_sites.items():
    for site in sites:
        norm_site = normalize(site)
        if norm_site in seen_normalized:
            continue
        seen_normalized.add(norm_site)
        
        status = "Added" if norm_site in current_normalized else "New"
        
        difficulty = "Medium"
        reason = "Requires investigation"
        
        # Difficulty heuristics
        if category == "Cam Models":
            difficulty = "Hard"
            reason = "Live streams often require specialized headers/cookies or have heavy obfuscation (M3U8 sniffing)"
        elif category == "Hentai Manga / Comics" or "manhwa" in norm_site or "manga" in norm_site:
            difficulty = "Impossible"
            reason = "Kodi addon is for video, not image viewers"
        elif category == "Leak Sites":
            difficulty = "Medium/Hard"
            reason = "Often use various file hosts or specialized players"
        elif category == "Streaming & Video Tubes":
            difficulty = "Easy/Medium"
            reason = "Standard BS4 parsing usually works; check for known players"
            
        # Specific overrides
        if "hub" in norm_site or "porn" in norm_site or "tube" in norm_site:
            if status == "New":
                difficulty = "Easy"
                reason = "Likely a standard tube site with BS4-parsable video tags"

        results.append({
            "site": site,
            "category": category,
            "status": status,
            "difficulty": difficulty,
            "reason": reason
        })

results.sort(key=lambda x: (x["status"] != "New", x["difficulty"]))

with open("new_site_candidates.json", "w") as f:
    json.dump(results, f, indent=4)

print(f"Total sites analyzed: {len(results)}")
print(f"New sites found: {len([r for r in results if r['status'] == 'New'])}")

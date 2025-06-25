def sort_condense(ivs: "list[tuple[int, int]]"):
    if len(ivs) == 0:
        return []
    if len(ivs) == 1:
        if ivs[0][0] > ivs[0][1]:
            return [(ivs[0][1], ivs[0][0])]
        else:
            return ivs
    eps: "list[tuple[int,bool]]" = []
    for iv in ivs:
        eps.append((min(iv), False))
        eps.append((max(iv), True))
    eps.sort()
    ret: "list[tuple[int, int]]" = []
    i = level = 0
    while i < len(eps) - 1:
        if not eps[i][1]:
            level = level + 1
            if level == 1:
                left = eps[i][0]
        else:
            if level == 1:
                if not eps[i + 1][1] and eps[i + 1][0] == eps[i][0] + 1:
                    i = i + 2
                    continue
                right = eps[i][0]
                ret.append((left, right))
            level = level - 1
        i = i + 1
    ret.append((left, eps[len(eps) - 1][0]))
    return ret


ffmpeg_supported_extensions = {
    # Video Containers
    "video": [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".flv",
        ".webm",
        ".m4v",
        ".ts",
        ".mpg",
        ".mpeg",
        ".wmv",
        ".3gp",
        ".ogv",
        ".rm",
        ".rmvb",
        ".vob",
    ],
    # Audio Containers
    "audio": [".mp3", ".aac", ".wav", ".flac", ".ogg", ".oga", ".m4a", ".wma", ".opus", ".ac3", ".amr", ".aiff"],
    # Image Formats
    "image": [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"],
    # Subtitle Formats
    "subtitle": [".srt", ".ass", ".ssa", ".vtt", ".sub"],
    # Raw Streams / Special Formats
    "raw": [".h264", ".h265", ".yuv", ".pcm"],
    # Network/Streaming Protocols (not file extensions, but supported inputs)
    # "protocol": ["rtmp://", "udp://", "tcp://", "http://", "https://"],
}

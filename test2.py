import pafy

url = "https://www.youtube.com/watch?v=bMt47wvK6u0"
video = pafy.new(url)

best = video.getbest()
best.download(quiet=True, callback= )
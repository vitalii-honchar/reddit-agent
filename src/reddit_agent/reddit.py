import praw

reddit = praw.Reddit(
    client_id="YI4E_yCx-V8U2zvNKJhSow",
    client_secret="m06OOl3KbMgibGVhrj1x9KTchbWHZw",
    user_agent="my user agent",
)

print(reddit.read_only)


submissions = reddit.subreddit("Startup_Ideas").search(
    query="pain",
    sort="hot",
    time_filter="month"
)

for submission in submissions:
    print(submission)
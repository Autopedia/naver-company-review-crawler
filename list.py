import json

with open("review.json", "r") as fp:
    reviews = json.load(fp)

for review in reviews:
    review['review'] = review['review']
    review['len'] = len(review['review'])

reviews = sorted(reviews, key=lambda k: k['len'], reverse=True)

data = []

for review in reviews:
    if review['len'] < 10:
        break
    data.append(review)

with open("review_v2.json", "w") as fp:
    json.dump(reviews, fp, indent=4, ensure_ascii=False)
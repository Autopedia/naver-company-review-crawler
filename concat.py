import pickle
import json
import pandas as pd
import csv

reviews = []

for i in range(2):
    with open(f"review{i}.plk", "rb") as fp:   # Unpickling
        origin = pickle.load(fp)
    print(len(origin))
    reviews.extend(origin)

# with open("reviews.plk", "wb") as fp:   #Pickling
#     pickle.dump(reviews, fp)

final = []

for review in reviews:
    tmp = {
        "naver_id": review[0],
        "review": review[2]
    }
    final.append(tmp)

with open("review.json", "w") as fp:
    json.dump(final, fp, ensure_ascii=False)

# df = pd.DataFrame(reviews, columns=column)
# df.to_json("review_final.json", orient="records")
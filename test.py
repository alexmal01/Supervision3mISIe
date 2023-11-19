import json
import pandas as pd

sekcje = pd.read_csv("sekcje_format.csv", sep=";", header=0)
sekcje = sekcje[~sekcje["nazwa_sekcji"].isin(["Działalność i wyniki operacyjne", "System zarządzania", "Profil ryzyka", "Wycena do celów wypłacalności", "Zarządzanie kapitałem"])]


id_name = dict(zip(list(sekcje["id_sekcji"]), list(sekcje["nazwa_sekcji"])))
name_id = dict(zip(list(sekcje["nazwa_sekcji"]), list(sekcje["id_sekcji"])))



def main():

    with open("headers.json", "r") as f:
        headers = json.load(f)

    # If sections_present key is a list with elements of depth both A.1, and A.1.1, choose the one with more dots
    for i in range(len(headers["header"])):
        if len(headers["sections_present"][i])>1:
            deepest = max([len(x.split(".")) for x in headers["sections_present"][i]])
            headers["sections_present"][i] = [x for x in headers["sections_present"][i] if len(x.split("."))==deepest]
    
    # Group by config (size, font, color) and get how many different sections are present for that config
    config_dict = {}
    for i in range(len(headers["header"])):
        config = (headers["size"][i], headers["color"][i], headers["font"][i])
        if config not in config_dict:
            config_dict[config] = set()
        config_dict[config].update(headers["sections_present"][i])

    config_dict = {k: len(v) for k, v in config_dict.items()}

    df = pd.DataFrame(headers)
    df["sections_present"] = df["sections_present"].apply(lambda x: x[0])
    df["tuple"] = df.apply(lambda x: (x["size"], x["color"], x["font"]), axis=1)
    df["num_ocs"] = df["tuple"].map(config_dict)
    df['header'] = df['sections_present'].map(id_name).combine_first(df['header'])
    df['id_sekcji'] = df['sections_present'].map(name_id).combine_first(df['sections_present']).apply(lambda x: x.replace(" ", "").strip())
    df['id'] = df.merge(sekcje, how="left", left_on="id_sekcji", right_on="id_sekcji")["id"]
        


    # for i in range(len(headers["header"])):
    #     headers["header"][i] = id_name.get(headers["sections_present"][i], headers["header"][i])
    
    # If there are multiple rows with the same sections_present, choose the one with the highest num_ocs value
    df = df.sort_values(by=["id", "num_ocs"], ascending=False)
    df = df.drop_duplicates(subset=["id"], keep="first")
    print(df)
    df.to_csv("headers.csv", index=False)
    


    # In the dataframe, if there are multiple rows with the same scetions_present, choose the one with the highest size column
    # df = df.sort_values(by=["sections_present", "size"], ascending=False)
    # df = df.drop_duplicates(subset=["sections_present"], keep="first")
    # print(df)

if __name__ == "__main__":
    main()
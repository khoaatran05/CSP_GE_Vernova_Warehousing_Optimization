import pandas as pd
import numpy as np
import regex



def empty_slot_filter(file):
    df = pd.read_excel(file)

    # Conventions to include in accurate report:
    # Racks - AA, BB, CC, B, C, D, E, F, G, H, J, K, L, M, N, O, P, QQ, RR,
    # TT, Q, R, S, T, U, V, XX, X, YY, Y, ZZ, Z, SMI, AEC, BEC, CEC, EEC, DEC,
    # FEC, GEC, HEC, REC, SPS, WMPS
    # Floor - A, REC, UU, (L/M/S).00.00.01, I, DOOR.FRONT
    # Other (exclude from project scope) - PPP, KANI, OE, OEP, OEC, INTHP, DOMPAL,
    # DOMPAO, WIP, QC, CAP

    # Standard Format for Locator Codes: YY.01.0A.01 (letter sequence at beginning
    # must match estblished rack/floor codes)

    # Remove any duplicate inventory slots
    df = df.drop_duplicates(subset = ["Location"], keep = "first")

    # Remove any entries that are outside of our project scope
    df = df[~(df["Location"].str.strip().str.contains(r"(PPP|KANI|OE|OEP|OEC|INTHP|DOMPAL|DOMPAO|WIP|QC|CAP)", regex = True))]

    # Label entries as either valid/invalid depending on locator code
    # Valid if it is an existent locator code in the warehouse; Invalid otherwise
    df["Entry Status"] = np.where(~(df["Location"].str.strip().str.contains(r"[A-Z]{1,3}\.[0-9]{2}\.[0-9][A-Z]\.[0-9]{2}", regex = True)), "Invalid", "Valid")

    # Identify locations that correspond to rack locator codes
    df["Rack Locations"] = np.where(df["Location"].str.strip().str.contains(r"(AA|BB|CC|QQ|RR|TT|XX|YY|ZZ|[B-H]{1}|[J-Z]{1})\.[0-9]{2}\.[0-9][A-Z]\.[0-9]{2}", regex = True), "Rack",
        np.where(df["Location"].str.strip().str.contains(r"(AEC|BEC|CEC|EEC|DEC|FEC|GEC|HEC|SPS|WMPS|PS|SMI)\.[0-9]{2}\.[0-9][A-Z]\.[0-9]{2}", regex = True), "Rack", "Non-Rack"))

    # Identify locations that correspond to floor locator codes
    df["Floor Locations"] = np.where(df["Location"].str.strip().str.contains(r"(L|M|S)\.00\.00.[0-9]{2}", regex = True), "Floor",
        np.where(df["Location"].str.strip().str.contains(r"(REC|UU|DOOR\.FRONT)", regex = True), "Floor",
            np.where(df["Location"].str.strip().str.contains(r"I\.[0-9]{2}\.00\.0{1,2}", regex = True), "Floor",
                np.where(df["Location"].str.strip().str.contains(r"I\.[0-9]{1,2}\.[A-Z]{1}\.[0-9]{1}", regex = True), "Floor",
                    np.where(df["Location"].str.strip().str.contains(r"A\.[0-9]{2}\.[0-9][A-Z]\.[0-9]{2}", regex = True), "Floor", "Non-Floor")))))


    # Create a new column to identify each locator code as either a rack or floor space
    # If netiher, locator code will be set as "Other"
    df["Inventory Type"] = np.where(df["Floor Locations"] == "Floor", "Floor", np.where(df["Rack Locations"] == "Rack", "Rack", "Other"))

    df = df.sort_values(by = "Location", ascending = True).reset_index()
    df = df.drop(["Rack Locations", "Floor Locations","index"], axis = 1)

    df.to_excel("sorted_empty_inventory.xlsx", index = False)
    return df



# Set file variable as personal path name for empty inventory report
file = "emptyLocations.xlsx"
print(empty_slot_filter(file))

import pandas as pd 
df  = pd.read_csv('/Users/francis/Desktop/5507Seminar_Model/DataBase/Data_Source.csv')

base = df[
    (df["con1"] == 1) &
    (df["fin25e2"] == 1) &
    (df["fin25e3"].isin([1, 2, 3])) &
    (df["con21"].isin([1, 2]))
].copy()

print("Base N:", len(base))

variables = ["age", "female", "educ", "inc_q", "emp_in", "urbanicity",
             "internet_use", "con9", "account", "dig_account", "con23"]
for var in variables:
    print("\n", "=" * 30)
    print(var)

    print(
        base[var]
        .value_counts(dropna=False)
        .sort_index()
    )

    print("Non-missing unique values:")
    print(base[var].dropna().unique())

    print("Missing N:", base[var].isna().sum())
    print("Unique N:", base[var].nunique(dropna=True))
    dig_by_country = (
    base
    .groupby("economycode")
    .agg(
        N=("dig_account", "size"),
        valid_dig_account=("dig_account", "count"),
        unique_dig_account=("dig_account", "nunique"),
    )
)

dig_by_country["missing"] = (
    dig_by_country["N"]
    - dig_by_country["valid_dig_account"]
)

print(dig_by_country)

w = base["wgt"]
print(len(base), ((base["con21"] == 1) * w).sum() / w.sum())   # expected: 16472, about 0.286
c = base[(base["con21"] == 1) & (base["con22"].isin([1, 2]))]
print(len(c), ((c["con22"] == 1) * c["wgt"]).sum() / c["wgt"].sum())  # expected: 4828, about 0.091

base["con9"] = base["con9"].where(base["con9"].isin([1, 2]))
ctrl = ["age", "female", "educ", "inc_q", "emp_in", "urbanicity",
        "internet_use", "con9", "account"]
common = base.dropna(subset=ctrl)
print(len(common), common["economycode"].nunique())
print((common["con21"] == 1).sum(), ((common["con21"] == 1) & common["con22"].isin([1, 2])).sum())

dropped = sorted(set(base["economycode"]) - set(common["economycode"]))
print(dropped)
sub = base[base["economycode"].isin(dropped)]
print(len(sub), (sub["con21"] == 1).sum(), ((sub["con21"] == 1) & (sub["con22"] == 1)).sum())
print(sub[ctrl].isna().sum())

base["inc_q_model"] = base["inc_q"]
base.loc[base["economycode"] == "LSO", "inc_q_model"] = 1   # LSO has no income data: fill a constant, absorbed by the country FE
ctrl = ["age", "female", "educ", "inc_q_model", "emp_in", "urbanicity",
        "internet_use", "con9", "account"]
common = base.dropna(subset=ctrl)
print(len(common), common["economycode"].nunique())
print(((common["con21"] == 1) & common["con22"].isin([1, 2])).sum())
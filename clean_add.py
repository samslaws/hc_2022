import numpy as np
import pandas as pd

hc_data = pd.read_csv('hc_data_2022.csv')
corrections = pd.read_csv('Corrections.csv')

financial_outreach = corrections[corrections['notes'] == 'financial outreach']
new_cols = set(list(financial_outreach['column_name']))
financial_outreach_update = financial_outreach.loc[:, ['firm_id', 'firm_name', 'column_name', 'new_data_point_numeric', 'non_survey']]

for x in new_cols:
    financial_outreach_update[x] = np.nan

financial_outreach_update = financial_outreach_update.reset_index(drop=True)

firm_ids = set(list(financial_outreach['firm_id']))
col_names = list(financial_outreach_update['column_name'])

i = 0
for index, row in financial_outreach_update.iterrows():
    financial_outreach_update[col_names[i]][i] = financial_outreach_update['new_data_point_numeric'][i]
    i += 1

financial_outreach_update = financial_outreach_update.rename(columns = {'firm_name': 'decipher_name'})
financial_outreach_update = financial_outreach_update.groupby(['firm_id', 'decipher_name']).sum(min_count=1)

edits = financial_outreach_update.loc[financial_outreach_update['non_survey'] == 0]
adds = financial_outreach_update.loc[financial_outreach_update['non_survey'] >= 1]

col_names_set = list(set(col_names))

edits = edits.reset_index()
adds = adds.reset_index()

adds = adds[['firm_id', 'decipher_name', 'fin2021_grossrev_globe', 'fin2021_netinc_globe', 'hc2021_eq_globefte', 'hc2021_total_globefte']]

hc_data = pd.concat([hc_data, adds])

hc_data = hc_data.reset_index(drop=True)

for row in edits.iterrows():
    firm_id = row[1]['firm_id']
    grossrev = row[1]['fin2021_grossrev_globe']
    netinc = row[1]['fin2021_netinc_globe']
    eq = row[1]['hc2021_eq_globefte']
    total = row[1]['hc2021_total_globefte']

    if np.isnan(grossrev) == False:
        hc_data.loc[hc_data['firm_id'] == firm_id, 'fin2021_grossrev_globe'] = grossrev

    else:
        pass

    if np.isnan(netinc) == False:
        hc_data.loc[hc_data['firm_id'] == firm_id, 'fin2021_netinc_globe'] = netinc

    else:
        pass

    if np.isnan(eq) == False:
        hc_data.loc[hc_data['firm_id'] == firm_id, 'hc2021_eq_globefte'] = eq

    else:
        pass

    if np.isnan(total) == False:
        hc_data.loc[hc_data['firm_id'] == firm_id, 'hc2021_total_globefte'] = total

    else:
        pass

d = hc_data
d_est = pd.read_csv("Global Headcount 2022 Worksheet - list_for_globalheadcount_estimates.csv")

d['hc_globe_all'] = d.filter(regex="^hc2021.*globehc$").drop(columns=["hc2021_total_globehc"]).sum(axis=1) + d[['hc_only_nonpart_total', 'hc_only_part_total']].sum(axis=1)
d['hc_globe_status'] = "submitted"

for row in d_est.iterrows():
	firm_id = row[1]['firm_id']
	firm_name = row[1]['firm_name']
	international = row[1]['international']
	hc_only_bin = row[1]['hc_only_bin']
	globe_est = row[1]['2022_global_attorneys']

	if international == 1:
		if hc_only_bin == 2:
			d.loc[d['firm_id'] == firm_id, 'hc_globe_all'] = globe_est
			d.loc[d['firm_id'] == firm_id, 'hc_globe_est'] = "predicted"
		else:
			tmp = pd.DataFrame({
				'firm_id':[firm_id],
				'decipher_name':[firm_name],
				'hc_globe_all':[globe_est],
				'hc_globe_est':["predicted"]
				})
			d = pd.concat([d, tmp], ignore_index=True)
	elif international == 0:
		if firm_id not in d['firm_id'].tolist():
			print(firm_id)
			tmp = pd.DataFrame({
				'firm_id':[firm_id],
				'decipher_name':[firm_name],
				'hc_globe_all':[globe_est],
				'hc_globe_est':['predicted']
				})
			d = pd.concat([d, tmp], ignore_index=True)

d.to_csv('hc_data_2022_globe_est.csv', index=False)

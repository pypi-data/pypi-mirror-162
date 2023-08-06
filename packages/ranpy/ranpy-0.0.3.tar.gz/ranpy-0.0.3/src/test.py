import ranpy as rp

R = rp.Ranpy(2022)

blah = R.get_beta({'alpha': 0.5, 'beta': 0.5})

print(blah.rvs(100))
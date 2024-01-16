import scipy as sp

cad = sp.genfromtxt('modump_list')
tjd = sp.genfromtxt('modump_tjd')

idx_sort = sp.argsort(cad)
cad = cad[idx_sort]
tjd = tjd[idx_sort]

#print(sp.diff(cad))

idx_end_interval = sp.where(sp.diff(cad) > 1)[0]
idx_start_interval = idx_end_interval + 1

idx_start_interval = sp.r_[0,idx_start_interval]
idx_end_interval = sp.r_[ idx_end_interval, len(cad) - 1]

dt = tjd[idx_end_interval] - tjd[idx_start_interval]
print(sp.c_[ cad[idx_start_interval], cad[idx_end_interval], dt ])
sp.savetxt('modump_tjd_intervals.txt',sp.c_[tjd[idx_start_interval],
                                            tjd[idx_end_interval]])

import scipy as sp
import matplotlib.pyplot as plt


infiles = ['sap_stats.txt','pdc_stats.txt',
          'psf_stats.txt']#,'circ6_stats.txt',
          #'circ8_stats.txt','circ10_stats.txt']

F,( (ax1,ax2,ax3),(ax4,ax5,ax6) ) = plt.subplots(2,3)
cuse = ['k','g','b','c','m','r']
labeluse = ['sap','pdc','psf','cir6','circ8','cir10']
for ii,ifile in enumerate(infiles):
    tmag,s1,es1,s2,es2,sigma,ks,p = sp.genfromtxt(ifile,unpack=1)

    ax1.errorbar(tmag,s1,es1,fmt='.',color=cuse[ii])
    ax2.errorbar(tmag,s2,es2,fmt='.',color=cuse[ii])
    ax3.plot(tmag,sigma,'.',color=cuse[ii])
    ax4.plot(tmag,ks,'.',color=cuse[ii])
    ax5.plot(tmag,p,'.',color=cuse[ii],label=labeluse[ii])

ax5.legend()
ax4.set_yscale('log')
ax5.set_yscale('log')
ax3.set_yscale('log')
F.set_size_inches(16,16)
F.tight_layout()


F2,( (ax1a,ax2a,ax3a),(ax4a,ax5a,ax6a) ) = plt.subplots(2,3)

pdc_tmag,pdc_s1,pdc_es1,pdc_s2,pdc_es2,pdc_sigma,pdc_ks,pdc_p = sp.genfromtxt('pdc_stats.txt',unpack=1)

for ii,ifile in enumerate(infiles):
    if ifile == 'pdc_stats.txt':
        continue
    tmag,s1,es1,s2,es2,sigma,ks,p = sp.genfromtxt(ifile,unpack=1)

    ax1a.plot(pdc_s1,s1,'.',color=cuse[ii])
    ax2a.plot(pdc_s2,s2,'.',color=cuse[ii])
    ax3a.plot(pdc_sigma,sigma,'.',color=cuse[ii])
    ax4a.plot(pdc_ks,ks,'.',color=cuse[ii])
    ax5a.plot(pdc_p,p,'.',color=cuse[ii],label=labeluse[ii])


ax4a.set_yscale('log')
ax5a.set_yscale('log')
ax3a.set_yscale('log')
ax4a.set_xscale('log')
ax5a.set_xscale('log')
ax3a.set_xscale('log')
ax5a.legend()
F2.set_size_inches(16,16)
F2.tight_layout()

plt.show()

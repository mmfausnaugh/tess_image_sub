import numpy as np
from scipy.spatial import KDTree
from scipy.ndimage import maximum_filter
import  photutils  as phot
import matplotlib.pyplot as plt
from copy import deepcopy
import os
import re


class PixelStamp(object):
    def __init__(self, image_array):
        self.image = image_array

        self.rowdim,self.coldim = np.shape(self.image)

        self.C,self.R = np.meshgrid(np.r_[0:self.rowdim],
                                    np.r_[0:self.coldim])

        #measured from ixexam...
        #self.sigma = 1.3

        #adjusted until fit my smoothed PRF models in one go
        #of order 8--10% error of enclosed volume, max pixel is 0.6%
        #of encloused volume
        self.sigma = 1.65


    def estimate_bkg(self, pixels,bkg_percentile=25):
        #formula  from source extractor guide
        bkg_arr = np.ravel(pixels[pixels > 0])
        bkg_level = np.percentile(bkg_arr, [bkg_percentile] )
        #print(bkg_level, len(bkg_arr[ bkg_arr < bkg_level]), len(bkg_arr))
        bkg_arr = bkg_arr[
            bkg_arr < bkg_level
        ]
        bkg = 2.5*np.median( bkg_arr ) - 1.5*np.mean(bkg_arr)
        return bkg_arr, bkg_level, bkg

    def estimate_bkg_diff_image(self, pixels):
        #formula  from source extractor guide
        bkg_arr = np.ravel(pixels)
        bkg = 2.5*np.median( bkg_arr ) - 1.5*np.mean(bkg_arr)
        return bkg_arr, bkg

    def compute_phot(self, aperture_mask, bkg_mask,bkg_percentile = 25, 
                     plot=False,
                     diff = False):

        if diff:
            bkg_arr, bkg = self.estimate_bkg_diff_image(self.image[bkg_mask])
            bkg_level = 0
        else:
            bkg_arr, bkg_level, bkg = self.estimate_bkg(self.image[bkg_mask],
                                                        bkg_percentile = bkg_percentile)

        flux_arr = (self.image - bkg).astype(float)
        norm = np.sum(flux_arr*aperture_mask)
        #print(len(aperture_mask[aperture_mask > 0]), int(norm), int(bkg), np.around(norm/bkg,3))
        centroid_row = np.sum(flux_arr*self.R*aperture_mask)/norm
        centroid_col = np.sum(flux_arr*self.C*aperture_mask)/norm

        centroid_row = centroid_row - self.rowdim/2.0 + 0.5
        centroid_col = centroid_col - self.coldim/2.0 + 0.5

        if plot:

            F,axes = plt.subplots( 2,2 )
            p_im = axes[0,0].imshow(self.image - bkg,
                                    cmap='viridis',
                                    origin='lower')
            plt.colorbar(p_im,ax=axes[0,0]
            )
            axes[0,0].plot(centroid_col + self.coldim/2.0 - 0.5,
                           centroid_row + self.rowdim/2.0 - 0.5,
                           'ro',ms=4)
            


            #print(centroid_col + self.coldim/2.0 - 0.5,
            #      centroid_row + self.rowdim/2.0 - 0.5,)
            level2 = np.percentile( np.ravel(flux_arr[flux_arr > 0]), [25])
            axes[0,0].contour(self.C, 
                              self.R,
                              self.image - bkg,
                              levels=[0,  bkg_level - bkg],
                              colors=['w','r'])
            axes[0,0].set_title('bkg subtracted scene')
            
            axes[0,1].barh( 
                np.r_[0:self.rowdim],
                np.mean(self.image - bkg,axis=1  ),
                height=1.0,
            )
            
            axes[1,0].bar( 
                np.r_[0:self.coldim],
                np.mean( self.image - bkg,axis=0 ),
                width=1.0
            )

            #axes[1,1].hist(np.ravel(self.image[bkg_mask]))
            axes[1,1].hist(bkg_arr)
            l,h = axes[1,1].get_ylim()
            axes[1,1].plot([bkg,bkg], [l,h], 'k',label='bkg estimate')
            axes[1,1].plot([bkg_level, bkg_level], [l,h], 'r',
                           label = 'pixels above \n{} percentile\nexcluded'.format(bkg_percentile) )
            axes[1,1].legend(fontsize=8)
            axes[1,1].get_ylim()

            
            plt.show()

        return norm, np.sum(bkg*aperture_mask), centroid_col, centroid_row

    def circle_phot(self,col,row):
        #see https://photutils.readthedocs.io/en/stable/pixel_conventions.html
        #for coordinate convention
        #it is 0,0 = center of lower left pixel
        a1 = phot.CircularAperture( (col,row),r = 3)
        a2 = phot.CircularAperture( (col,row),r = 4)
        a3 = phot.CircularAperture( (col,row),r = 5)
        pt1 = phot.aperture_photometry(self.image, a1, method='subpixel',subpixels=5)
        pt2 = phot.aperture_photometry(self.image, a2, method='subpixel',subpixels=5)
        pt3 = phot.aperture_photometry(self.image, a3, method='subpixel',subpixels=5)
        b1 = phot.CircularAnnulus( (col,row),r_in=8 , r_out= 12)
        bmask = b1.to_mask(method='center')
        bkg_arr = np.ravel(bmask.multiply(self.image))
        bkg_arr = bkg_arr[ abs(bkg_arr) != 0 ] 
        bkg = 2.5*np.median( bkg_arr ) - 1.5*np.mean(bkg_arr)
        bkg1 = a1.area*bkg
        bkg2 = a2.area*bkg
        bkg3 = a3.area*bkg

        return pt1['aperture_sum'].data[0] - bkg1, bkg1, pt2['aperture_sum'].data[0] - bkg2, bkg2, pt3['aperture_sum'].data[0] - bkg3, bkg3

    def small_circle_phot(self,col,row):
        a1 = phot.CircularAperture( (col,row),r = 1)
        a2 = phot.CircularAperture( (col,row),r = 2)
        a3 = phot.CircularAperture( (col,row),r = 3)
        pt1 = phot.aperture_photometry(self.image, a1, method='subpixel',subpixels=5)
        pt2 = phot.aperture_photometry(self.image, a2, method='subpixel',subpixels=5)
        pt3 = phot.aperture_photometry(self.image, a3, method='subpixel',subpixels=5)
        b1 = phot.CircularAnnulus( (col,row),r_in=8 , r_out= 12)
        bmask = b1.to_mask(method='center')
        bkg_arr = np.ravel(bmask.multiply(self.image))
        bkg_arr = bkg_arr[ abs(bkg_arr) != 0 ] 
        bkg = 2.5*np.median( bkg_arr ) - 1.5*np.mean(bkg_arr)
        bkg1 = a1.area*bkg
        bkg2 = a2.area*bkg
        bkg3 = a3.area*bkg

        return pt1['aperture_sum'].data[0] - bkg1, bkg1, pt2['aperture_sum'].data[0] - bkg2, bkg2, \
            pt3['aperture_sum'].data[0] - bkg3, bkg3

    def lots_of_small_circle_phot(self,col,row):
        aperature_radii = np.r_[0.25:2.25:0.25]
        aperatures = [phot.CircularAperture( (col,row), r = rad) for rad in aperature_radii]
        #a1 = phot.CircularAperture( (col,row),r = 1)
        #a2 = phot.CircularAperture( (col,row),r = 2)
        pts = [ phot.aperture_photometry(self.image, a, method='subpixel',
                                         subpixels=5) for a in aperatures]
        b1 = phot.CircularAnnulus( (col,row),r_in=8 , r_out= 12)
        bmask = b1.to_mask(method='center')
        bkg_arr = np.ravel(bmask.multiply(self.image))
        bkg_arr = bkg_arr[ abs(bkg_arr) != 0 ] 
        bkg = 2.5*np.median( bkg_arr ) - 1.5*np.mean(bkg_arr)
        bkg = np.array([a.area*bkg for a in aperatures ])
        phot_out = np.array([ pt['aperture_sum'].data[0] for pt in pts])
        return phot_out - bkg, bkg, 


    def select_annulus_pixels(self,rad_1,rad_2):
        #grab pixels ISIS style----if pixel is between rad_1 and
        #rad_2, select it
        
        mid_c = self.coldim//2 
        mid_r = self.rowdim//2 
        R = np.sqrt( (self.C - mid_c)**2 + (self.R - mid_r)**2)
        mask = (R >= rad_1) & (R <= rad_2)
        return mask

    
    def estimate_SNR(self,bkg):
        subtracted_image = (self.image - bkg).astype(float)

        #e_bkg = np.sqrt(bkg)
        #e_source = np.sqrt(subtracted_image)

        #assumes no read noise or dark current
        #and that bias has been removed
        SNR = subtracted_image/np.sqrt(self.image)
        #SNR = subtracted_iamge/np.sqrt(subtracted_image + bkg)
        return SNR


    def gaussian(self, col,row):
        #print(self.R, row)
        #print(self.C, col)
        gaussian = np.exp(- (self.R - row)**2/self.sigma**2 -  
                          (self.C - col)**2/self.sigma**2   )
        gaussian = gaussian/gaussian.sum()
        return gaussian

    def fit_scene(self, 
                  source_col, 
                  source_row,
                  bkg, threshold=5,
                  plot=False,
                  diagnostic_plots=False):
        #print(source_col, source_row)
        #testing source detection
        #sig_pixels = self.fit_scene(r1 + self.rowdim/2.0 ,
        #                            c1 + self.coldim/2.0,
        #                            bkg, threshold = 10)
        #axes[0,0].plot(np.ravel(self.C[sig_pixels]),
        #               np.ravel(self.R[sig_pixels]),
        #               'co',ms=4)



        #assumes no read noise or dark current
        #and that bias has been removed
        if (self.image <= 0).any():
            imuse = deepcopy(self.image)
            mask_bad = imuse <= 0
            imuse[mask_bad ] = 1
            subtracted_image = (imuse - bkg).astype(float)
            error_image = np.sqrt(imuse)
            error_image[mask_bad] = 1.e15
        else:
            subtracted_image = (self.image - bkg).astype(float)
            error_image = np.sqrt(self.image)
        #put in for PRF fitting
        #error_image = 0.001*np.ones(np.shape(subtracted_image))

        SNR = subtracted_image/error_image
        pixels = self.threshold_pixels(SNR, threshold)

        star_rows = []
        star_cols = []

        removed_rows = []
        removed_cols = []

        flag = 0

        templates = []
        templates.append( self.gaussian(source_col, 
                                        source_row) )


        try:
            B = self.do_fit(subtracted_image, error_image, templates)
        except np.linalg.LinAlgError as e:
            print(e)
            pass

        scene = 0
        for ii in range(len(B)):
            scene += B[ii,0]*templates[ii]

        

        SNR = (subtracted_image - scene)/error_image
        #print('volume, max:', np.sum(abs(SNR*error_image)) , np.ravel(SNR*error_image).max() )
        pixels = self.threshold_pixels(SNR, threshold)
        if (pixels == False).all():
            flag = 1

        while flag == 0:
            #fit the object and a gaussian at the highest SNR point
            #two center, centroid in a 3x3
            #print(star_rows)

            max_pix = SNR == SNR[pixels].max()

            max_c = self.C[max_pix][0]
            max_r = self.R[max_pix][0]

            #flag2 = 0
            #while flag2 == 0:
            #    if max_c == 0 or max_c  == self.coldim or \
            #       max_c == 1 or max_c  == self.coldim - 1 or \
            #       max_r == 1 or max_r  == self.rowdim - 1 or \
            #       max_r == 0 or max_r == self.rowdim:
            #        pixels[max_pix] = False
            #    
            #        max_pix = SNR == SNR[pixels].max()
            #        max_c = self.C[max_pix][0]
            #        max_r = self.R[max_pix][0]
            #
            #    else:
            #        flag2 = 1


            r_slice = slice(max_r - 1, max_r + 2)
            c_slice = slice(max_c - 1, max_c + 2)
            s1_sub = subtracted_image[r_slice, c_slice]
            
            s1_c = np.sum(s1_sub * self.C[r_slice, c_slice])/np.sum(s1_sub)
            s1_r = np.sum(s1_sub * self.R[r_slice, c_slice])/np.sum(s1_sub)


            if s1_c < 0 or s1_c > self.coldim or \
               s1_r < 0 or s1_r > self.rowdim:
                removed_rows.append(max_r)
                removed_cols.append(max_c)
                for z in zip(removed_rows,removed_cols):
                    #print(z)
                    SNR[z] = 0


                if len(removed_rows) > 10:
                    flag =1
                continue

            #print(delta_r)
            star_rows.append(s1_r)
            star_cols.append(s1_c)


            if diagnostic_plots:
                plt.imshow(SNR, origin='lower')
                plt.plot(source_col, source_row,'bo',ms=4)
                plt.plot(star_cols, star_rows,'ro',ms=2)
                plt.plot(star_cols[-1], star_rows[-1],'mo',ms=2)
                plt.show()
            
            templates = []
            templates.append( self.gaussian(source_col, 
                                            source_row) )
            for z in zip(star_cols, star_rows ):
                templates.append( self.gaussian(z[0], z[1] ) )

            #template = self.gaussian(s1_c, s1_r) + self.gaussian(source_col, source_row)

            if np.isnan(subtracted_image).any() or np.isinf(subtracted_image).any():
                print('sub image')
            if np.isnan(error_image).any() or np.isinf(error_image).any():
                print('error image')
            if np.isnan(templates).any() or np.isinf(templates).any():
                print('templates')

            Btmp = self.do_fit(subtracted_image, error_image, templates)
            #print(Btmp)
            if Btmp[0,0] == 0:
                star_cols.pop()
                star_rows.pop()

                removed_cols.append(max_c)
                removed_rows.append(max_r)

            else:
                B = Btmp


            scene = 0
            for ii in range(len(B)):
                scene += B[ii,0]*templates[ii]

            SNR = (subtracted_image - scene)/error_image
            #print('volume, max:', np.sum( abs(SNR*error_image) ), np.ravel(SNR*error_image).max() )
            pixels = self.threshold_pixels(SNR, threshold)

            for z in zip(removed_rows,removed_cols):
                #print(z)
                SNR[z] = 0

            #print(star_rows)
            if len(star_rows) + len(removed_rows) > 10:
                flag = 1
            if (pixels == False).all():
                flag = 1


        if B[0,0] > 0:
            mag = -2.5*np.log10(B[0,0]/600/0.8/0.99) + 20.44
            #print(B[0,0], mag)
        else:
            mag = 99
            #print(B[0,0])

        if plot == True:
            F,(  (ax1,ax2),
                 (ax3, ax4),
                 (ax5, ax6)) = plt.subplots(3,2)
            
            vlow,vhigh = np.percentile(np.ravel(subtracted_image),
                                       [5,95])
            ax1.imshow(subtracted_image,
                       vmin = vlow, vmax = vhigh,
                       origin='lower')
            ax2.imshow(scene,
                       vmin = vlow, vmax = vhigh,
                       origin='lower')
            ax3.imshow(subtracted_image - scene,
                       vmin = vlow, vmax = vhigh,
                       origin='lower')
            c = ax4.imshow(SNR,
                             origin='lower')
            plt.colorbar(c,label='N$\sigma$')

            ax1.plot(source_col, source_row,'bo')
            ax2.plot(source_col, source_row,'bo')
            ax3.plot(source_col, source_row,'bo')
            ax4.plot(source_col, source_row,'bo')
            ax1.plot(star_cols, star_rows,'ro',ms=2,zorder=4)
            ax2.plot(star_cols, star_rows,'ro',ms=2,zorder=4)
            ax2.text(source_col, source_row,'{:.2f}'.format(mag), fontsize = 8,
                     color='c')


            
            
            sector = re.search("sector(\d\d)",os.getcwd())
            sector = int( sector.group(1) )
            if sector < 27:
                exptime = 1800
            elif sector < 56:
                exptime = 600
            else:
                exptime = 200

            for jj in range(len(star_cols)):
                Tmag_use = -2.5*np.log10(B[jj + 1,0]/exptime/0.8/0.99) +20.44
                ax2.text(star_cols[jj], star_rows[jj],'{:.2f}'.format(Tmag_use), 
                         fontsize=6,
                         color='r')
            ax3.plot(star_cols, star_rows,'ro',ms=2,zorder=4)
            ax4.plot(star_cols, star_rows,'ro',ms=2,zorder=4)
            
            m = subtracted_image < np.percentile(np.ravel(subtracted_image),[85])
            N,bins,_ = ax5.hist(np.ravel(subtracted_image[m]),50)
            ax6.hist(np.ravel(subtracted_image - scene), bins)

            l1,h1 = ax5.get_ylim()
            l2,h2 = ax6.get_ylim()
            if h2 > h1:
                h = h2
            else:
                h = h1
            l = 0
                
            ax5.plot([0,0],[l,h],'k--')
            ax5.set_ylim([l,h])
            
            ax6.plot([0,0],[l,h],'k--')
            ax6.set_ylim([l,h])
            
            
            l,h = ax5.get_xlim()
            ax6.set_xlim([l,h])
                
            ax1.set_title('subtracted image')
            ax2.set_title('model of scene')
            ax3.set_title('residuals')
            ax4.set_title('SNR of residuals')
            ax5.set_title('data')
            ax6.set_title('residuals')
                
#            F.set_size_inches(8,6)
            F.set_size_inches(12,12)
            F.tight_layout()
            
            plt.show()
                
                        
        return B[0,0]

    def do_fit(self, subtracted_image, error_image, templates):
        data = np.ravel(subtracted_image)
        weights = np.ravel(error_image)
        A = np.zeros(len(templates))
        C = np.zeros((  len(templates),len(templates) ))

        for ii in range(len(templates)):
            model = np.ravel(templates[ii])
            
            A[ii] =    np.sum(data*model/weights**2) 
            for jj in range(len(templates)):
                model2 = np.ravel(templates[jj])
                C[ii,jj] = np.sum(model*model2/weights**2)

        try:
            B = np.matrix(C).I*np.matrix(A).T
        except np.linalg.LinAlgError:
            #print('error in linalg!',C,A)
            print('error in linalg!')
            B = np.zeros(len(A)).reshape(  (1,len(A))  )

        return B


    def threshold_pixels(self, SNR, threshold):
        pixels = SNR > threshold
        pixels[0:2,:] = False
        pixels[self.rowdim - 3:,:] = False
        pixels[:,0:2] = False
        pixels[:,self.coldim - 3:] = False

        return pixels

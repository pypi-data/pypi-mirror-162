"""
Created on Tue Jun 28 12:11:26 2022

@author: swainasish@yahoo.com
spatialCDR version : 0.0.8
"""

#%%
import numpy as np
import pandas as pd 
import time 
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge,RidgeCV
from sklearn.feature_selection import VarianceThreshold

#%%
class SpotDeconvolution:
    def __init__(self):
        pass
    
    def preprocessing(self,sc_array,st_array,sc_genes,st_genes,n_hvgs=1000):
        
        '''
        Find High Variance Common genes between Single cell and Spatial data

        Preprocess the Single cell and  Spatial data for further Modules 
        
        
        Parameters 
        ---------------------------------------------------------------------
        
        | sc_array : Matrix of Single cell data [ rows are the cells and columns are the genes ] 
        | st_array : Matrix of Spatial data [rows are the cells and columns are the genes]   
        | sc_genes : Gene names of the sc_array matrix 
        | st_genes : Gene names of the st_array matrix 
        | n_hvgs : (default=1000) Number of high variance genes consider for analysis
        '''
           
        t1_pre = time.time()
        #Find common genes between SC and ST data 
        sc_df,st_df =  pd.DataFrame(sc_array),pd.DataFrame(st_array)
        sc_df.columns,st_df.columns = sc_genes,st_genes
        common_genes =  np.intersect1d(sc_df.columns,st_df.columns)
        sc_df = sc_df.loc[:,common_genes]

        
        #Finding 1000 high variance genes in sc_genes 
        n_genes = len(sc_df.columns)
        if n_genes < n_hvgs:
            st_df = st_df.loc[:,common_genes]
        else: 
            sc_vars = sc_df.var().to_numpy()
            sorted_variance_indexes = np.argsort(sc_vars)[::-1]
            top_hvg_index = sorted_variance_indexes[0:n_hvgs]
            hvgs = sc_df.columns[top_hvg_index]
            sc_df = sc_df.loc[:,hvgs]
            st_df = st_df.loc[:,hvgs]
    
        
        t2_pre = time.time()
        
        print(f"""\n Pre-processing Done \n Took {t2_pre - t1_pre} seconds, retained {len(sc_df.columns)} High variable genes
              """)
        
        return sc_df,st_df
    
    def __random_spot_generator__(self,sc_arr_pro,sc_cell_type_labels,min_cell=5,max_cell=10):
        sc_arr_pro = np.array(sc_arr_pro)
        sc_cell_type_labels = np.array(sc_cell_type_labels)
        n_cell, n_gene = sc_arr_pro.shape
        
        #generate random cell number 
        random_cell_number = np.random.randint(low = min_cell, high=max_cell+1)
        
        #pick random rows in sc_data 
        
        random_indexes = np.random.choice(n_cell,random_cell_number)  
        random_sc_arrays = sc_arr_pro[random_indexes,:]
        random_sc_arrays = random_sc_arrays.sum(axis=0)
        
        random_sc_labels = sc_cell_type_labels[random_indexes]
        ct,ct_count = np.unique(random_sc_labels,return_counts=True)
        ct_perct = ct_count/np.sum(ct_count)
        label_dic = {}
        for i in range(len(ct)):
            label_dic[ct[i]]=ct_perct[i]
    
        
        return random_sc_arrays,label_dic
    
        
 
    
    def simulate_st_spots(self,sc_arr_pro,sc_cell_type_labels,min_cell=5,max_cell=10):
        
        """ This function generate spatial_spots from the single cell data 
            Using three scenarios mentioned in the paper 
            
            Parameters
            -------------------------------------------------------------------
            
            | sc_arr_pro : single data output from preprocessing function
            | sc_cell_type_labels : Cell type annotations of single cell data (now of sc_data rows = length of labels)
            | min_cell : (default = 5) Minium number of cell a spot have 
            | max_cell : (default = 10) Maxium number of cell a spot have 
            
            
        """
            
        
        t1_simu = time.time()
        
        # Convert datas to numpy array 
        sc_arr_pro = np.array(sc_arr_pro)
        sc_cell_type_labels = np.array(sc_cell_type_labels)
        
        
        n_cell, n_gene = sc_arr_pro.shape
        n_spot_to_simulated = 6*n_cell
        unique_cell_types = np.unique(sc_cell_type_labels)

        simulated_st_array = np.zeros([n_spot_to_simulated,n_gene])
        simulated_ct_prop = pd.DataFrame(np.zeros([n_spot_to_simulated,len(unique_cell_types)]))
        simulated_ct_prop.columns = unique_cell_types
        
        
        count=0
        
        #Scenario.1 - Each spot having only one celltype

        
        print("Simulate Spatial Data : 0%")
        
        for i in range(3*n_cell):
            random_cell_number = np.random.randint(low = min_cell, high=max_cell+1)
            
            #random_cell_type_pick
            random_cell_type = np.random.choice(unique_cell_types)
            cell_type_indexes = np.where(sc_cell_type_labels==random_cell_type)[0]
            
            #pick the indexes from the sc data
            index_to_pick = np.random.choice(cell_type_indexes,random_cell_number)
            random_array_frame = sc_arr_pro[index_to_pick,:]
            spot_1 = random_array_frame.sum(axis=0)
            simulated_st_array[count,:] = spot_1
            simulated_ct_prop.loc[count,random_cell_type] = 1
            
            count +=1
        t2_simu  = time.time()
        
        print(F"Simulate Spatial Data : 50% , Took {t2_simu-t1_simu} Seconds ")
        
        
        # Scenario.2 - Each spot comprise of 2 cell type 
        if max_cell <= 2:   #designed for slideseq
            for i in range(2*n_cell):
                sc_array , ct_dic = self.__random_spot_generator__(sc_arr_pro,sc_cell_type_labels,min_cell=0,max_cell=max_cell)
                simulated_st_array[count,:] = sc_array
                for i in ct_dic.keys():
                    simulated_ct_prop.loc[count,i]=ct_dic[i]
                count=count+1
        else:
            for i in range(2*n_cell):
                ct1,ct2 = np.random.choice(unique_cell_types,2)
                ct1_array_index = np.where(ct1==sc_cell_type_labels)[0]
                ct2_array_index = np.where(ct2==sc_cell_type_labels)[0]
                
                random_cell_number = np.random.randint(low = min_cell, high=max_cell+1)
                ct1_cell_num = int(random_cell_number/2)
                ct2_cell_num = int(random_cell_number - ct1_cell_num)
                
                ct1_index_to_pick = np.random.choice(ct1_array_index,ct1_cell_num)
                ct2_index_to_pick = np.random.choice(ct2_array_index,ct2_cell_num)
                concate_indexes = [*ct1_index_to_pick,*ct2_index_to_pick]
                
                array_frame = sc_arr_pro[concate_indexes,:]
                array_frame = array_frame.sum(axis=0)
                ct_prop = {}
                ct_prop[ct1] = ct1_cell_num / random_cell_number
                ct_prop[ct2] = ct2_cell_num / random_cell_number  
                
                simulated_st_array[count,:] = array_frame
                for i in ct_prop.keys():
                    simulated_ct_prop.loc[count,i]=ct_prop[i]
                
                count= count+1
                
        t3_simu = time.time()
        print(F"Simulate Spatial Data : 85% , Took {t3_simu-t1_simu} Seconds ")
        
        
        #Scenario-3 Each spot comprise of random cell type composition 
        for i in range(n_cell):
            random_cell_number = np.random.randint(low = min_cell, high=max_cell+1)
            random_indexes = np.random.choice(n_cell,random_cell_number)
            random_sc_df = sc_arr_pro[random_indexes,:]
            random_sc_label=sc_cell_type_labels[random_indexes]
            
            random_sc_df_sum = random_sc_df.sum(axis=0)
            ct,ct_count = np.unique(random_sc_label,return_counts=True)
            ct_count = ct_count/sum(ct_count)
            
            simulated_st_array[count,:]=random_sc_df_sum
            
            for i in range(len(ct)):
                simulated_ct_prop.loc[count,ct[i]]=ct_count[i]
            
            count = count + 1
            
            
            
    
        
            
            
        t4_simu = time.time()
        print(F"100% Data Simulated,  {simulated_ct_prop.shape[0]} Spots Generated , Took {t4_simu-t1_simu} Seconds ")
        
        return simulated_st_array,simulated_ct_prop
    
    
    def __normalisation__(self,df):
        df = np.sqrt(df)        #Power Transformation
        norm = StandardScaler()
        df = norm.fit_transform(df)  #Standarization

        return df
    
    
    def __chunk_df__(self,df,label,n):
        n_cell,n_gene = df.shape
        df = np.array(df)
        label = np.array(label)
        if n_cell < n:
            pass
        else:
            random_points = np.random.randint(0,n_cell,n)
            df = df[random_points,:]
            label= label[random_points,:]
        return df,label 
    
    def fit(self,simu_st_array,simu_st_prop):
        
        """
        Fit the ridge regression model between simulated Spatial data and spatial  proportions
        
        Parameters
        -----------------------------------------------------------------------
        | simu_st_array : Simulated ST array output from simulate_st_spots functions
        | simu_st_prop : Simulated ST proportations output from simulate_st_spots functions
        
        Output
        -----------------------------------------------------------------------
        Best fitted parameters from ridge regressions
        """
        
        self.__simu_st_array_norm__ = self.__normalisation__(simu_st_array)
        
        #finding best param for ridge regression 
        chunk_sc, chunk_label = self.__chunk_df__(self.__simu_st_array_norm__,simu_st_prop,3000)
        regr_cv = RidgeCV(alphas=[0.1, 1.0,10.0,20.0,50.0,100,300,500,1000,2000,2500,5000,10000,15000,20000,30000,50000,100000],
                  alpha_per_target=True)
        model_cv =regr_cv.fit(chunk_sc, chunk_label)
        self.__best_alpha__ = model_cv.alpha_
        self.__simu_st_prop__ = simu_st_prop
        
        
        return self.__best_alpha__
    
    

    
    def predict(self,st_data,return_prop = True, return_low_exp_celltypes = False,cell_prop_threshold = 0.05):
        
        """
        Predict the cell type proportations from the Spatial data 
        
        Parameters
        ----------------------------------------------------------------------
        st_data : st_data output from the preprocessing function 
        return_low_exp_celltypes  : low expressed cell proportions needed or not
        cell_prop_threshold : Threshold for low expression celltype
            
        """

        model = Ridge(alpha=self.__best_alpha__)
        
        self.__simu_st_array_norm__ = np.random.normal(self.__simu_st_array_norm__)
        
        model.fit(self.__simu_st_array_norm__, self.__simu_st_prop__)
        
        st_data = self.__normalisation__(st_data)
        predict = model.predict(st_data)
        
        #modification 
        
        #0 if it's less than 0.09 ~ 0.1
        predict[predict<0] = 0 
        row_sum = predict.sum(axis=1).reshape(-1,1)
        predict = predict / row_sum
        
        predict = pd.DataFrame(predict)
        predict.columns = self.__simu_st_prop__.columns
        
        if return_prop == False:
            predict = predict.idxmax(axis=1)
            #predict = pd.get_dummies(predict)
        if return_prop ==True:
            if return_low_exp_celltypes == False:
                row_sum_high_thres = np.sum(predict>=cell_prop_threshold,axis=1)
                for row in range(predict.shape[0]):
                    if row_sum_high_thres[row] > 1:
                        predict.loc[row,predict.iloc[row,:]<cell_prop_threshold]=0
                        x = predict.iloc[row,:]/sum(predict.iloc[row,:])
                        predict.iloc[row,:] = x 
            else:
                pass
        
        
                    
                    
                    
            
            
            
        
            
        
        return predict

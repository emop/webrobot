from taobao import Taobao

def test_get_detail(num_iid):
    pass
    
def test_get_cate_list(pid):
    pass
    
    
if __name__ == '__main__':
    api = Taobao('12395385', '53697d99eccd670191af0603d7256f77')
    #data = api.taobao_itemcats_get(fields='cid,parent_cid,name,is_parent', parent_cid=0)
    data = api.taobao_item_get(fields='detail_url,num_iid,title,nick,type,cid,seller_cids,props,input_pids,input_str,desc,pic_url,num,valid_thru,list_time,delist_time,stuff_status,location,price,post_fee,express_fee,ems_fee,has_discount,freight_payer,has_invoice,has_warranty,has_showcase,modified,increment,approve_status,postage_id,product_id,auction_point,property_alias,item_img,prop_img,sku,video,outer_id,is_virtual', 
    num_iid='4735623930')
    print data
    
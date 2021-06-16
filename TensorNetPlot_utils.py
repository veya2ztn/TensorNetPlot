
def get_chain_mps(name,Tensor_Type,num=4,layer=2,vertical=False,**kargs):
    mps1=GridGraph(name)
    l_bra = '├─' if vertical else '─┬─'
    r_bra = '─┤' if vertical else '─┴─'
    bdirc = 'ulrd' if vertical else 'ludr'
    for j in range(layer):
        for i in range(num):
            if   j ==       0:
                mps1.add_node(Tensor_Type(f"{i}{j}",[2]+[3]+[2],bra_direction=l_bra,**kargs))
            elif j == layer-1:
                mps1.add_node(Tensor_Type(f"{i}{j}",[2]+[3]+[2],bra_direction=r_bra,**kargs))
            else:
                mps1.add_node(Tensor_Type(f"{i}{j}",[2]+[3]+[3]+[2],bond_direction=bdirc,**kargs))
        for i1,i2 in zip(range(num-1),range(1,num)):
            #print(f"{i1}{j}",f"{i2}{j}")
            mps1.add_edge((f"{i1}{j}",-1),(f"{i2}{j}",0))

    for j1,j2 in zip(range(layer-1),range(1,layer)):
        for i in range(num):
            mps1.add_edge((f"{i}{j1}",-2),(f"{i}{j2}",1))
    return mps1
def contract_TN(TN_list,connections,name=None):
    new_name = '+'.join([TN.name for TN in TN_list]) if name is None else name
    new_TN   = GridGraph(new_name)
    for TN in TN_list:
        for new_name, new_node in TN.nodes.items():
            assert new_name not in new_TN.nodes
            new_TN.nodes[new_name] = new_node
        for source_c,target_c in connections:
            new_TN.add_edge(source_c,target_c)
    return new_TN

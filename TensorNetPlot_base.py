import plotly.graph_objects as go
import numpy as np

class Bond:
    x=y=length=partner=thickness=None
    def __init__(self,host,idx_in_host,dim,relvent_dirc,direction=np.array((0,1))):
        self.host      = host
        self.idx       = idx_in_host
        self.nickname  = f"b{idx_in_host}"
        self.dim       = dim
        self.direction = direction
        self.relvent_dirc = relvent_dirc
        self.layoutQ   = False

    @property
    def pos(self):
        return np.array([self.x,self.y])
    @property
    def name(self):
        return f"{self.host.name}_{self.nickname}"
    @property
    def orientation(self):
        try:
            direction = self.direction if self.partner is None else self.direction - self.partner.direction
            direction = direction/np.linalg.norm(direction)
        except:
            print(self.direction)
            print(self.partner.direction)
            raise
        return direction

    @property
    def x0(self):return self.x
    @property
    def y0(self):return self.y
    @property
    def x1(self):
        new_pos = self.pos + self.length*self.orientation
        return new_pos[0]

    @property
    def y1(self):
        new_pos = self.pos + self.length*self.orientation
        return new_pos[1]

    def default_color(self):
        color = '#EF553B' #if self.color == "default" else self.color
        bond_kargs   = {"fillcolor":color,'line_color':color}
        return bond_kargs

    def set_postion(self,x,y=None,update=False):

        if y is not None:

            if self.x is not None and (self.layoutQ and not update):
                assert self.x == x
                assert self.y == y
            else:
                self.x = x
                self.y = y
        else:
            if self.x is not None and (self.layoutQ and not update):

                assert self.x == x[0]
                assert self.y == x[1]
            else:
                self.x = x[0]
                self.y = x[1]
        self.layoutQ = True

    def set_partner(self,partner):
        assert self.dim==partner.dim
        if self.partner is not None and self.partner != partner:
            print(f'one bond can only have one paired bond, not the pair is {self.partner.name} but you assign {partner.name}')
        self.partner        = partner

    def __repr__(self):
        strings = f'''Bond:{self.name}|D=({self.dim})|O={self.relvent_dirc}->{self.direction} link_bond:{self.partner.name if self.partner else None} pos:{(self.x,self.y)}'''
        return strings

    def deploy(self,fig=None,show_name=False,**kargs):
        xc = (self.x0 + self.x1)/2
        yc = (self.y0 + self.y1)/2
        bond_kargs = kargs['bond_kargs'] if 'bond_kargs' in kargs else self.default_color()
        if fig is not None and show_name:fig.add_annotation(x=xc , y=yc,text=self.name,showarrow=False)
        return go.Scatter(x=[self.x0,self.x1],y=[self.y0,self.y1],mode='lines', fill="toself",
                          text=f"B={self.dim}",hoveron='points',hoverinfo='text',**bond_kargs)

class TN_Tensor:
    '''
    this module create a tensor object with
    -internal property:
     - rank
     - dim per rank
    '''
    x = y = z = None
    type_name = "Tensor"
    vertex_num= None
    def __init__(self,name,dims=(2,3,2),bond_direction=None,bra_direction="─┬─",color="default",**kargs):
        self.dims             = dims
        self.nickname         = name
        self.layoutQ          = False
        self.host             = None
        self.color            = color
        self.bond_direction   = self.set_direction(bra_direction) if bond_direction is None else bond_direction
        self.bond_orientation = self.set_orientation(self.bond_direction)
        self.bonds = [Bond(self,i,dim,dirc,direction) for i,(dim,dirc,direction) in enumerate(zip(dims,self.bond_direction,self.bond_orientation))]

    def num_of_bonds_for(self,d):return self.bond_direction.count(d)

    @property
    def num_of_u_bonds(self):return self.bond_direction.count('u')
    @property
    def num_of_d_bonds(self):return self.bond_direction.count('d')
    @property
    def num_of_r_bonds(self):return self.bond_direction.count('r')
    @property
    def num_of_l_bonds(self):return self.bond_direction.count('l')

    def set_orientation(self,direction):
        return [self.orientation_map(symbol) for symbol in direction]
    @property
    def name(self):
        if self.host:
            return f"{self.host}_{self.nickname}"
        return self.nickname
    @property
    def free_bond_index(self):
        return [i for i,bond in enumerate(self.bonds) if bond.partner is None]
    @property
    def bond_direction_string(self):
        #↖↑↗ ←↔→ ↙↓↘
        out=""
        for i in range(self.rank):
            if i in self.free_bond_index:
                out+=self.bond_direction[i]
            else:
                out+='·'

        out=out.replace('u','↑')
        out=out.replace('d','↓')
        out=out.replace('l','←')
        out=out.replace('r','→')
        return out
    @property
    def rank(self):
        return len(self.dims)


    @property
    def x_end(self):
        if self.x is None:
            return None
        else:
            return self.x + self.w
    @property
    def y_end(self):
        if self.y is None:
            return None
        else:
            return self.y + self.h

    @property
    def free_rank(self):
        return self.rank  - len(self.children)- len(self.parents)

    @property
    def pos(self):
        if self.x is None:
            raise ValueError("the layout is not initialize, please set self.x self.y self.z before call pos")
        if self.z is None:
            return [self.x,self.y]
        else:
            return [self.x,self.y,self.z]

    @property
    def market(self):
        if self.rank == 1:
            marker=dict(symbol='circle',
                    size=15,
                    color='#DB4551',    #'#DB4551',
                    line=dict(color='rgb(50,50,50)', width=1)
                    )
        else:
            marker=dict(symbol='square',
                        size=30,
                        color='#6175c1',    #'#DB4551',
                        line=dict(color='rgb(50,50,50)', width=1)
                        )
        return marker

    @property
    def contracted_bonds(self):
        return [bond for bond in self.bonds if bond.partner is not None]

    @property
    def link_nodes(self):
        return [bond.partner.host.name for bond in self.contracted_bonds]

    def default_color(self):
        tensor_kargs   = {"fillcolor":'#3366CC','line_color':'#3366CC'}
        return tensor_kargs
    def shape_vertex_pos(self):
        raise NotImplementedError

    def add_link(self,target_bond):
        source_bond.set_partner(target_bond)

    def assign_host(self,host_name):
        self.host = host_name

    def set_all_vertex_and_bond(self,all_vertex,bond_length,**kargs):
        self.vertex_pos = all_vertex
        for bond,pos in zip(self.bonds, all_vertex[-len(self.bonds):]):
            bond.set_postion(pos,**kargs)
            bond.length=bond_length
        
    def __repr__(self):
        d_string = ",".join([str(d) for d in self.dims])
        strings = f'''{self.type_name}:{self.name}|({d_string}) {self.bond_direction_string} link_nodes:{self.link_nodes} pos:{(self.x,self.y)}->{(self.x_end,self.y_end)}'''
        return strings

class Graph:
    def __init__(self,name,name_nodes=[],edges=[]):
        self.name      = name
        self.nodes     = {}
        #self.edges     = []
        self.add_nodes(name_nodes)
        self.add_nodes(edges)

    @property
    def bonds(self):
        bonds = []
        for name, node in self.nodes.items():
            bonds+=node.bonds
        return bonds


    @property
    def bonds_map(self):
        return dict((bond.name,bond) for bond in self.bonds)

    @property
    def edges(self):
        edges = dict([[ ",".join(list(set([bond.name,bond.partner.name]))) ,[bond.name,bond.partner.name]]for bond in self.bonds if bond.partner is not None])
        return edges.values()
    def add_node(self,node,hostQ=True):
        if hostQ:
            node.assign_host(self.name)
        self.nodes[node.name]=node

    def add_nodes(self,name_nodes):
        for node in name_nodes:
            name = node.name
            if name in self.nodes:print(f"warning: you reset a existed node:{name}")
            self.add_node(name,node)

    def convert_bond(self,bond_obj):
        if isinstance(bond_obj,Bond):
            return bond_obj
        elif isinstance(bond_obj,list) or isinstance(bond_obj,tuple):
            node, bond_idx = bond_obj
            node = self.convert_node(node)
            return node.bonds[bond_idx]
        elif isinstance(bond_obj,str):
            node     = self.bonds_map[bond_obj].host
            bond_idx = [b.name for b in node.bonds].index(bond_obj)
            return node.bonds[bond_idx]
        else:
            print('!Not accepted format')
            raise NotImplementedError

    def convert_node(self,node_name):
        if isinstance(node_name,str):
            node_name = f"{self.name}_{node_name}" if node_name not in self.nodes else node_name
            return self.nodes[node_name]
        return node_name

    def add_edge(self,source_bond,target_bond):
        source_bond = self.convert_bond(source_bond)
        target_bond = self.convert_bond(target_bond)
        #self.edges.append([source_bond.name,target_bond.name])
        source_bond.set_partner(target_bond)
        target_bond.set_partner(source_bond)


    def add_edges(self,edges):
        for source,target in edges:
            self.add_edge(source,target)

class GridGraph(Graph):

    def cat(self,next_graph,connections):
        for new_name, new_node in next_graph.nodes.items():
            assert new_name not in self.nodes
            self.nodes[new_name] = new_node
        #self.edges += next_graph.edges
        for source_c,target_c in connections:
            self.add_edge(source_c,target_c)

    def layout(self,start_point=(0,0),bond_width=1,bond_length=1,spacing=1):
        first_node = list(self.nodes.keys())[0]
        first_node =self.nodes[first_node]
        first_node.set_location(start_point,0,bond_width=bond_width,bond_length=bond_length)
        self.Recursion_layout(first_node,bond_width=bond_width,bond_length=bond_length,spacing=spacing)
        self.Recursion_layout(first_node,bond_width=bond_width,bond_length=bond_length,spacing=spacing)

    def Recursion_layout(self,now_node,bond_width=1,bond_length=1,spacing=1):
        if not now_node.layoutQ:
            print(now_node)
            raise
        for now_bond in now_node.contracted_bonds:
            next_bond = now_bond.partner
            next_node = next_bond.host

            if not next_node.layoutQ:
                if not next_bond.layoutQ:
                    now_pos = now_bond.pos
                    new_pos = now_pos + spacing*now_bond.orientation
                    # print(now_bond)
                    # print(f"now_pos:{now_pos} -> orientation:{now_bond.orientation} -> new_pos:{new_pos}")
                    next_bond.set_postion(new_pos)
                the_layouted_bond_idx = next_bond.idx
                next_node.set_postion_from_bond(the_layouted_bond_idx,bond_width=bond_width,bond_length=bond_length)
                self.Recursion_layout(next_node,bond_width=bond_width,bond_length=bond_length,spacing=spacing)

    def reset_layout(self):
        for bond in self.bonds:bond.layoutQ=False
        for node in self.nodes.values():node.layoutQ = False

    def free_bond(self,direction):
        return [bond for bond in self.bonds if (bond.partner is None and bond.relvent_dirc==direction)]

    def default_color(self):
        color = '#1F77B4' #if self.color == "default" else self.color
        contract_kargs = {"fillcolor":color,'line_color':color}
        return contract_kargs

    def depoly(self,fig=None,**kargs):
        bonds_map = self.bonds_map
        ### depoly contract bond
        objects=[]
        for source_bond,target_bond in self.edges:
            bond1 = bonds_map[source_bond]
            bond2 = bonds_map[target_bond]
            contract_kargs = kargs['contract_kargs'] if 'contract_kargs' in kargs else self.default_color()
            objects.append(go.Scatter(x=[bond1.x0,bond2.x0], y=[bond1.y0,bond2.y0],mode='lines', fill="toself",
                          text=f"B={bond1.dim}",hoveron='points',hoverinfo='text',**contract_kargs))
            #fig.add_shape(type="line",x0=bond1.x0, y0=bond1.y0, x1=bond2.x0, y1=bond2.y0,line=dict(color="RoyalBlue",width=3))
        ### depoly Tensor
        for T_tensor in self.nodes.values():
            objects+=T_tensor.deploy(fig)
        return objects

    def draw(self,show_name=False,**kargs):
        fig = go.Figure()

        axis = dict(showline=False, zeroline=False,showgrid=False,showticklabels=False,)
        fig.update_layout(showlegend=False,xaxis=axis,yaxis=axis,plot_bgcolor='white')
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="white",
                font_size=16,
                font_family="Rockwell"
            )
        )
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(scaleanchor = "x",scaleratio = 1,)
        objects = self.depoly(fig,show_name=show_name,**kargs)
        for obj in objects:fig.add_trace(obj)
        return fig

    def delte_contract(self,bond):
        bond = self.convert_bond(bond)
        bond1 = bond
        bond2 = bond.partner
        bond1.partner = None
        bond2.partner = None

    def delte_node(self,node):
        node = self.convert_node(node)
        for bond in node.bonds:
            bond.partner.partner = None
            bond.partner = None
        del self.nodes[node.name]

    def __repr__(self):
        strings = [f"-Node:{name}-> {val}" for name,val in self.nodes.items()]
        return "\n".join(strings)

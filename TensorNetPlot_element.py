from TensorNetPlot_base import *

class Rectangle_T(TN_Tensor):
    '''
    all use big
    '''
    type_name = "Rectangle"
    v1 = np.array([1,0])
    v2 = np.array([0,1])
    vertex_num = 4


    @property
    def shape_vertex_pos(self):
        x0 = self.x
        y0 = self.y
        w  = self.w
        h  = self.h
        v1 = self.v1
        v2 = self.v2
        pos0= np.array([self.x,self.y])
        pos1= pos0 + 0*v1 + h*v2
        pos2= pos0 + w*v1 + h*v2
        pos3= pos0 + w*v1 + 0*v2
        return np.stack([pos0,pos1,pos2,pos3])

    def orientation_map(self,symbol):
        v1=self.v1
        v2=self.v2
        orientation_map = {'u': v2,
                           'd':-v2,
                           'l':-v1,
                           'r': v1}
        return orientation_map[symbol]

    def set_direction(self,bra):
        assert self.rank > 1
        if (bra == '─┬─') or (bra == 'd'):
            return 'l'+'d' *(self.rank-2)+'r'
        if (bra == '─┴─') or (bra == 'u'):
            return 'l'+'u' *(self.rank-2)+'r'
        if (bra == '├─') or (bra == 'r'):
            return 'u'+'r' *(self.rank-2)+'d'
        if (bra == '─┤') or (bra == 'l'):
            return 'u'+'l' *(self.rank-2)+'d'
        raise NotImplementedError

    def get_all_vertex_relative(self,w,h,bond_distribution_on_side=None):
        v1 = self.v1
        v2 = self.v2
        now_r = now_d = now_u = now_l = 0
        pos    = np.array([0,0])
        pos_end= pos + w*v1 + h*v2
        if bond_distribution_on_side is None: bond_distribution_on_side = {}
        for d in 'ludr':
            if d not in bond_distribution_on_side:
                num_of_bonds_for_d = self.num_of_bonds_for(d)
                bond_distribution_on_side[d] = (np.arange(num_of_bonds_for_d)+1)/(num_of_bonds_for_d+1)
        all_vertex=[pos,pos + 0*v1 + h*v2, pos + w*v1 + h*v2, pos + w*v1 + 0*v2] # need to be same as self.vertex_num = 4
        for bond in self.bonds:
            d = bond.relvent_dirc
            if d=='r':
                new_pos = pos + w*v1*(1) + h*v2*bond_distribution_on_side[d][now_r]
                now_r+=1
            elif d=='d':
                new_pos = pos + w*v1*bond_distribution_on_side[d][now_d] + h*v2*(0)
                now_d+=1
            elif d=='u':
                new_pos = pos + w*v1*bond_distribution_on_side[d][now_u] + h*v2*(1)
                now_u+=1
            elif d=='l':
                new_pos = pos + w*v1*(0) + h*v2*bond_distribution_on_side[d][now_l]
                now_l+=1
            else:
                raise NotImplementedError
            all_vertex.append(new_pos)
        all_vertex = np.stack(all_vertex)
        assert len(all_vertex) == len(self.bonds) + self.vertex_num
        return all_vertex

    def set_postion_from_bond(self,bond_idx,bond_width=1,bond_length=1,**kargs):
        vertex_idx = bond_idx + self.vertex_num
        self.set_location(self.bonds[bond_idx].pos,vertex_idx,bond_width=bond_width,bond_length=bond_length,**kargs)

    def set_location(self,pos,vertex_idx,bond_width=1,bond_length=1,w=None,h=None,update=False,bond_distribution_on_side=None):
        w = bond_width*max(1,self.num_of_r_bonds,self.num_of_l_bonds) if w is None else w
        h = bond_width*max(1,self.num_of_u_bonds,self.num_of_d_bonds) if h is None else h

        all_vertex = self.get_all_vertex_relative(w,h,bond_distribution_on_side=bond_distribution_on_side)
        all_vertex = all_vertex - all_vertex[vertex_idx] + pos
        self.x,self.y   = all_vertex[0]
        self.w = w
        self.h = h
        self.set_all_vertex_and_bond(all_vertex,bond_length)
        self.layoutQ = True

    def default_color(self,_type):
        if _type == 'vector':return {"fillcolor":'#B6E880','line_color':'#B6E880'}
        if _type == 'matrix':return {"fillcolor":'#DC3912','line_color':'#DC3912'}
        color = '#3366CC' if self.color == "default" else self.color
        if _type == 'tensor':return {"fillcolor":color,'line_color':color}
        raise NotImplementedError


    def deploy(self,fig=None,show_name=False,**kargs):
        ### depoly Free bond
        objects=[bond.deploy(fig,**kargs) for bond in self.bonds if bond.partner is None]
        ### depoly Main Body
        x0=self.x;y0=self.y;x1=self.x_end;y1=self.y_end;
        xc = (x0+x1)/2
        yc = (y0+y1)/2
        if self.rank==1:
            vector_kargs = kargs['vector_kargs'] if 'vector_kargs' in kargs else self.default_color('vector')
            obj = go.Scatter(x=[xc],y=[yc],mode='points',fill="toself",
                            hoveron='fills',hoverinfo='text',text=f"D={self.dims}",
                            **vector_kargs)
        elif self.rank==2:
            matrix_kargs = kargs['matrix_kargs'] if 'matrix_kargs' in kargs else self.default_color('matrix')
            obj = go.Scatter(x=[x0,xc,x1,xc,x0],y=[yc,y1,yc,y0,yc],mode='lines',fill="toself",
                            hoveron='fills',hoverinfo='text',text=f"D={self.dims}",
                            **matrix_kargs)
        else:
            tensor_kargs = kargs['tensor_kargs'] if 'tensor_kargs' in kargs else self.default_color('tensor')
            obj = go.Scatter(x=[x0,x0,x1,x1,x0], y=[y0,y1,y1,y0,y0],mode='lines',fill="toself",
                           hoveron='fills',hoverinfo='text',text=f"D={self.dims}",
                           **tensor_kargs)
            if fig is not None and show_name:fig.add_annotation(x=xc , y=yc,text=self.name,showarrow=False)
        objects.append(obj)

        return objects

class OneSideBigRectangle_T(Rectangle_T):
    type_name = "OneSideBigRectangle_T"
    vertex_num = 4
    def set_postion_from_bond(self,bond_idx,bond_width=1,bond_length=1,**kargs):
        anchor_bond = self.bonds[bond_idx]
        same_direction_bond = [b for b in self.bonds if b.relvent_dirc == anchor_bond.relvent_dirc and b.partner]
        v1 = self.v1
        v2 = self.v2
        assert len(same_direction_bond) >1
        spacing = np.linalg.norm(anchor_bond.pos-anchor_bond.partner.pos)

        ## automatic detect
        if False in [b.partner.layoutQ for b in same_direction_bond]:
            #raise NotImplementedError("you must link this to full bond connection")
            return

        for next_bond in same_direction_bond:
            if next_bond.layoutQ:continue
            now_bond= next_bond.partner
            now_pos = now_bond.pos
            new_pos = now_pos + spacing*now_bond.orientation
            next_bond.set_postion(new_pos)

        #determine_the_orientation
        vector_of_this_line = same_direction_bond[0].pos-same_direction_bond[1].pos
        if np.dot(v2,vector_of_this_line)==0:
            orientation_horizon  = v1
            orientation_vertical = v2
        else:
            orientation_horizon  = v2
            orientation_vertical = v1

        lengthes=[]
        for b in same_direction_bond:
            anchor_node = b.partner.host
            lengthes += [np.dot(orientation_horizon,vertex) for vertex in anchor_node.shape_vertex_pos]
        max_length = max(lengthes)
        min_length = min(lengthes)

        length = max(lengthes) - min(lengthes)

        if anchor_bond.relvent_dirc in ['u','d']:
            w = length
            h = bond_width*max(1,self.num_of_r_bonds,self.num_of_l_bonds)
        elif anchor_bond.relvent_dirc in ['r','l']:
            w = bond_width*max(1,self.num_of_u_bonds,self.num_of_d_bonds)
            h = length

        self.w = w
        self.h = h

        distribution_ratio = [(np.dot(orientation_horizon,bond.pos)-min_length)/length for bond in same_direction_bond]
        bond_distribution_on_side = {}
        bond_distribution_on_side[anchor_bond.relvent_dirc] = distribution_ratio
        if  anchor_bond.relvent_dirc =='u':oppsite_direction = 'd'
        if  anchor_bond.relvent_dirc =='d':oppsite_direction = 'u'
        if  anchor_bond.relvent_dirc =='l':oppsite_direction = 'r'
        if  anchor_bond.relvent_dirc =='r':oppsite_direction = 'l'
        oppsite_direction_bond=[b for b in self.bonds if b.relvent_dirc == oppsite_direction and b.partner]
        if len(oppsite_direction_bond) == len(same_direction_bond):
            bond_distribution_on_side[oppsite_direction] = distribution_ratio

        bond = anchor_bond

        vertex_idx = self.vertex_num + bond_idx
        all_vertex = self.get_all_vertex_relative(w,h,bond_distribution_on_side=bond_distribution_on_side)
        all_vertex = all_vertex - all_vertex[vertex_idx] + bond.pos
        self.x,self.y   = all_vertex[0]

        self.set_all_vertex_and_bond(all_vertex,bond_length)
        self.layoutQ = True

class Flag_T(Rectangle_T):
    '''
              ■■■■■◣
              ■■■■■■◣
              ■■■■■■■■>
              ■■■■■■◤
              ■■■■■◤

    '''
    type_name = "Flag_T"
    v1 = np.array([1,0])
    v2 = np.array([0,1])
    vertex_num = 5
    def __init__(self,name,dims=(2,3,2),bond_direction=None,bra_direction="─┬─",main_direction="r",**kargs):
        super().__init__(name,dims=dims,bond_direction=bond_direction,bra_direction=bra_direction,**kargs)
        self.main_direction   = main_direction
        assert self.bond_direction.count(main_direction)==1

    def get_all_vertex_relative(self,w,h,bond_distribution_on_side=None):
        v1 = self.v1
        v2 = self.v2
        r_num = self.num_of_r_bonds
        d_num = self.num_of_d_bonds
        u_num = self.num_of_u_bonds
        l_num = self.num_of_l_bonds
        now_r = now_d = now_u = now_l = 0
        pos    = np.array([0,0])
        # r --> v1
        # u --> v2
        pos_end= pos + w*v1 + h*v2
        if   self.main_direction=='r':off_site=h/3*(+v1)
        elif self.main_direction=='d':off_site=w/3*(-v2)
        elif self.main_direction=='u':off_site=w/3*(+v2)
        elif self.main_direction=='l':off_site=h/3*(-v1)
        else:
            raise NotImplementedError
        shape_vertex=[pos,pos + 0*v1 + h*v2, pos + w*v1 + h*v2, pos + w*v1 + 0*v2] # need to be same as self.vertex_num = 4

        bond_vertex = []
        for bond in self.bonds:
            d = bond.relvent_dirc
            if d=='r':
                new_pos = pos + w*v1*(1) + h*v2*(now_r+1)/(r_num+1)
                now_r+=1
            elif d=='d':
                new_pos = pos + w*v1*(now_d+1)/(d_num+1) + h*v2*(0)
                now_d+=1
            elif d=='u':
                new_pos = pos + w*v1*(now_u+1)/(u_num+1) + h*v2*(1)
                now_u+=1
            elif d=='l':
                new_pos = pos + w*v1*(0) + h*v2*(now_l+1)/(l_num+1)
                now_l+=1
            else:
                raise NotImplementedError
            if d == self.main_direction:
                new_pos    = new_pos + off_site
                new_vertex_pos = new_pos
            bond_vertex.append(new_pos)
        shape_vertex.insert('lurd'.index(self.main_direction)+1,new_vertex_pos)
        all_vertex = shape_vertex + bond_vertex
        all_vertex = np.stack(all_vertex)
        assert len(all_vertex) == len(self.bonds) + self.vertex_num
        return all_vertex

    def deploy(self,fig,**kargs):
        ### depoly Free bond
        objects=[bond.deploy(fig,**kargs) for bond in self.bonds if bond.partner is None]
        ### depoly Main Body
        x0=self.x;y0=self.y;x1=self.x_end;y1=self.y_end;
        xc = (x0+x1)/2
        yc = (y0+y1)/2

        # main_direction_bond = [b for b in self.bonds if b.relvent_dirc == self.main_direction][0]
        # x_s,y_s     = main_direction_bond.pos
        # x=[x0,x0,x1,x1,x0];
        # y=[y0,y1,y1,y0,y0];
        # x.insert('lurd'.index(self.main_direction)+1,x_s)
        # y.insert('lurd'.index(self.main_direction)+1,y_s)
        x,y = self.vertex_pos[:self.vertex_num].transpose(1,0)
        tensor_kargs = kargs['tensor_kargs'] if 'tensor_kargs' in kargs else self.default_color('tensor')
        obj = go.Scatter(x=x,y=y,mode='lines',fill="toself",
                       hoveron='fills',hoverinfo='text',text=f"D={self.dims}",
                       **tensor_kargs
                        )

        objects.append(obj)

        return objects

class Circle_T(Rectangle_T):
    type_name = "Circle"
    v1 = np.array([1,0])
    v2 = np.array([0,1])
    vertex_num = 2
    def __init__(self,name,dims=(2,3,2),bond_direction=None,bra_direction="─┬─",**kargs):
        super().__init__(name,dims=dims,bond_direction=bond_direction,bra_direction=bra_direction,**kargs)
        for d in 'lurd':
            assert self.num_of_bonds_for(d) <= 1


    @property
    def shape_vertex_pos(self):
        x0 = self.x
        y0 = self.y
        w  = self.w
        h  = self.h
        v1 = self.v1
        v2 = self.v2
        pos0= np.array([self.x,self.y])
        pos1= pos0 + 0*v1 + h*v2
        pos2= pos0 + w*v1 + h*v2
        pos3= pos0 + w*v1 + 0*v2
        return np.stack([pos0,pos1,pos2,pos3])

    def num_of_bonds_for(self,d):return self.bond_direction.count(d)

    def get_all_vertex_relative(self,w,h,bond_distribution_on_side=None):
        v1      = self.v1
        v2      = self.v2
        r       = max(w,h)/2
        all_vertex=[np.array([ -r, -r]),np.array([ r, r])]

        for bond in self.bonds:
            d = bond.relvent_dirc
            if   d=='r':new_pos = np.array([ r, 0])
            elif d=='d':new_pos = np.array([ 0,-r])
            elif d=='u':new_pos = np.array([ 0, r])
            elif d=='l':new_pos = np.array([-r, 0])
            else:
                raise NotImplementedError
            all_vertex.append(new_pos)
        all_vertex = np.stack(all_vertex)
        assert len(all_vertex) == len(self.bonds) + self.vertex_num
        return all_vertex

    def deploy(self,fig,**kargs):
        ### depoly Free bond
        objects=[bond.deploy(fig,**kargs) for bond in self.bonds if bond.partner is None]
        ### depoly Main Body
        x0=self.x;y0=self.y;x1=self.x_end;y1=self.y_end;
        xc = (x0+x1)/2
        yc = (y0+y1)/2
        assert fig is not None
        x,y = self.vertex_pos[:self.vertex_num]
        x0,y0 = x
        x1,y1 = y
        tensor_kargs = kargs['tensor_kargs'] if 'tensor_kargs' in kargs else self.default_color('tensor')
        fig.add_shape(type="circle",xref="x", yref="y",x0=x0, y0=y0, x1=x1, y1=y1 ,**tensor_kargs)
        return objects

class Triangle_T(TN_Tensor):
    '''
    ------
    \    /
     \  /
    '''
    type_name = "Triangle_T"
    vertex_num = 3
    v1 = np.array([1,0])
    v2 = np.array([0,1])
    orientation_map = {'u':v2,
                       'l':-np.sin(np.pi/3)*v1 - np.cos(np.pi/3)*v2,
                       'r':+np.sin(np.pi/3)*v1 - np.cos(np.pi/3)*v2,
                       'd':-v2}
    def __init__(self,name,dims=(2,3,2),bond_direction='ldr',rotation=0,**kargs):
        theta = np.pi*rotation/180
        rotation_matrix = np.array([[np.cos(theta),np.sin(theta)],[-np.sin(theta),np.cos(theta)]])
        self.v1 = np.dot(rotation_matrix,self.v1)
        self.v2 = np.dot(rotation_matrix,self.v2)
        super().__init__(name,dims=dims,bond_direction=bond_direction,bra_direction=None)
        assert self.num_of_d_bonds <= 1
    @property
    def shape_vertex_pos(self):
        x0 = self.x
        y0 = self.y
        w  = self.w
        h  = self.h
        v1 = self.v1
        v2 = self.v2
        pos0= np.array([self.x,self.y])
        pos1= pos0 + 0*v1 + h*v2
        pos2= pos0 + w*v1 + h*v2
        pos3= pos0 + w*v1 + 0*v2
        return np.stack([pos0,pos1,pos2,pos3])

    def orientation_map(self,symbol):
        v1=self.v1
        v2=self.v2
        orientation_map = {'u':v2,
                           'l':-np.sin(np.pi/3)*v1 - np.cos(np.pi/3)*v2,
                           'r':+np.sin(np.pi/3)*v1 - np.cos(np.pi/3)*v2,
                           'd':-v2}
        return orientation_map[symbol]
    def default_color(self):
        color = '#1F77B4' if self.color == "default" else self.color
        contract_kargs = {"fillcolor":color,'line_color':color}
        return contract_kargs

    def get_all_vertex_relative(self,w1,w2,w3,bond_distribution_on_side=None):
        v1      = self.v1
        v2      = self.v2
        w       = max(w1,w2,w3)
        r       = w/2/np.cos(np.pi/6)
        pos1    = r*(-np.cos(np.pi/6)*v1+np.sin(np.pi/6)*v2)
        pos2    = r*(+np.cos(np.pi/6)*v1+np.sin(np.pi/6)*v2)
        pos3    = r*(-v2)
        all_vertex=[pos1,pos2, pos3] # need to be same as self.vertex_num = 4


        if bond_distribution_on_side is None: bond_distribution_on_side = {}
        for d in 'lur':
            if d not in bond_distribution_on_side:
                num_of_bonds_for_d = self.num_of_bonds_for(d)
                bond_distribution_on_side[d] = (np.arange(num_of_bonds_for_d)+1)/(num_of_bonds_for_d+1)
        now_l = now_r = now_d = now_u = 0
        for bond in self.bonds:
            d = bond.relvent_dirc
            if   d=='u':
                new_pos = pos1 + bond_distribution_on_side[d][now_l]*(pos2-pos1)
                now_l+=1
            elif d=='l':
                new_pos = pos3 + bond_distribution_on_side[d][now_d]*(pos1-pos3)
                now_d+=1
            elif d=='r':
                new_pos = pos2 + bond_distribution_on_side[d][now_r]*(pos3-pos2)
                now_r+=1
            elif d=='d':
                new_pos = pos3
            else:
                raise NotImplementedError
            all_vertex.append(new_pos)
        all_vertex = np.stack(all_vertex)
        assert len(all_vertex) == len(self.bonds) + self.vertex_num
        return all_vertex

    def set_postion_from_bond(self,bond_idx,bond_width=1,bond_length=1,**kargs):
        vertex_idx = bond_idx + self.vertex_num
        self.set_location(self.bonds[bond_idx].pos,vertex_idx,bond_width=1,bond_length=1,**kargs)

    def set_location(self,pos,vertex_idx,bond_width=1,bond_length=1,w=None,update=False,bond_distribution_on_side=None):
        if w is None:
            w1 = bond_width*max(1,self.num_of_u_bonds)
            w2 = bond_width*max(1,self.num_of_l_bonds)
            w3 = bond_width*max(1,self.num_of_r_bonds)
        elif isinstance(w,list) or isinstance(w,tuple):
            w1,w2,w3 = w
        else:
            w1=w2=w3 = w
        all_vertex = self.get_all_vertex_relative(w1,w2,w3,bond_distribution_on_side=bond_distribution_on_side)
        all_vertex      = all_vertex - all_vertex[vertex_idx] + pos
        self.w = w1
        self.h = w1
        self.x,self.y   = all_vertex[0]

        self.set_all_vertex_and_bond(all_vertex,bond_length)
        self.layoutQ = True

    def deploy(self,fig,show_name=False,**kargs):
        ### depoly Free bond
        objects=[bond.deploy(fig,**kargs) for bond in self.bonds if bond.partner is None]
        ### depoly Main Body
        x,y = self.vertex_pos[:self.vertex_num].transpose(1,0)
        tensor_kargs = kargs['tensor_kargs'] if 'tensor_kargs' in kargs else self.default_color()
        obj = go.Scatter(x=x, y=y,mode='lines',fill="toself",
                       hoveron='fills',hoverinfo='text',text=f"D={self.dims}",
                       **tensor_kargs)
        if fig is not None and show_name:fig.add_annotation(x=xc , y=yc,text=self.name,showarrow=False)
        objects.append(obj)
        return objects

class Triangle_AS_T(Triangle_T):
    '''
    ------
    \    /
     \  /
    '''
    type_name = "Triangle_AS"
    v1 = np.array([1,0])
    v2 = np.array([0,1])

    def __init__(self,name,dims=(2,3,2),bond_direction=None,main_direction="r",**kargs):

        if   main_direction =='r':
            rotation_angel = - 90
            bond_direction = 'uld' if bond_direction is None else bond_direction
        elif main_direction =='d':
            rotation_angel = 0
            bond_direction = 'ldr' if bond_direction is None else bond_direction
        elif main_direction =='l':
            rotation_angel = + 90
            bond_direction = 'dru' if bond_direction is None else bond_direction
        elif main_direction =='u':
            rotation_angel = +180
            bond_direction = 'rul' if bond_direction is None else bond_direction
        else:raise NotImplementedError
        super().__init__(name,dims=dims,bond_direction=bond_direction,rotation =rotation_angel, **kargs)
    def orientation_map(self,symbol):
        v1=self.v1
        v2=self.v2
        orientation_map = {'u': v2,'d':-v2,'l':-v1,'r': v1}
        return orientation_map[symbol]

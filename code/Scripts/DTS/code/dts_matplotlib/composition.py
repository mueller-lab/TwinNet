class SubfigureSingleColumn:

    def __init__(self, subplots_figure_, subplots_axis_array_):
        self.colnr=0
        self.subplots_figure=subplots_figure_
        self.subplots_axis_array=subplots_axis_array_
    
    def column_number_increase(self):
        self.colnr = self.colnr +1
        print( " .. column number set to", self.colnr )
        
    def subplots_axis_array_pointer_for_column(self, rownr_=0):

        return self.subplots_axis_array[self.colnr]
        
class SubfigurePerColumn:

    def __init__(self, subplots_figure_, subplots_axis_array_):
        self.colnr=0
        self.subplots_figure=subplots_figure_
        self.subplots_axis_array=subplots_axis_array_
    
    def column_number_increase(self):
        self.colnr = self.colnr +1
        print( " .. column number set to", self.colnr )
        
    def subplots_axis_array_pointer_for_column(self, rownr_=0):

        print( " .. rownr_=", rownr_, "self.colnr=", self.colnr )

        return self.subplots_axis_array[rownr_][self.colnr]
        

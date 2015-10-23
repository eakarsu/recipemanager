class RecipesController < ApplicationController

  def index
    @recipes = Recipe.all
  end
  
  def show
    @recipe = Recipe.find(params[:id])
  end
  
  def new
    @recipe = Recipe.new
  end
  
  def create
    #binding.pry
    @recipe = Recipe.new(recipe_params)
    @recipe.chef = Chef.find(1)
    if @recipe.save
      #do something
      flash[:success] =  "Tour recipe was created successfully"
      redirect_to recipes_path
    else
      render :new
    end
  end
  
  def edit
    @recipe = Recipe.find(params[:id])
  end
  
  def update
    @recipe = Recipe.find(params[:id])
    if @recipe.update(recipe_params)
      #do something
      flash[:success] =  "Your recipe was updated successfully"
      redirect_to recipe_path(@recipe)
    else
      render :edit
    end
  end
   
  private
    
    def recipe_params
      params.require(:recipe).permit(:name, :summary, :description, :picture)
    end
    
end
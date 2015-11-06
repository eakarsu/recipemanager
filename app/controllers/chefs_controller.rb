class ChefsController < ApplicationController
  before_action :set_chef,only: [:edit,:update,:show]
  before_action :require_same_user, only: [:edit,:update]
  
  def index
   # @recipes = Recipe.all.sort_by{|likes| likes.thumbs_up_total}.reverse
    @chefs = Chef.paginate(page: params[:page],per_page: 3)
  end
  
  def new
    @chef = Chef.new
  end

  def create
    #binding.pry
    @chef = Chef.new(chef_params)
    if @chef.save
      flash[:success] = "Your account was created successfully"
      session[:chef_id] = chef.id
      redirect_to recipes_path
    else
      render 'new'
    end
    
  end

  def edit
  end

  
  def update
    #binding.pry
    if @chef.update(chef_params)
      flash[:success] = "Your profile is updated successfully"
      redirect_to chef_path(@chef) #TO DO change to show chef page
    else
      render 'edit'
    end
  end

  def show
    @recipes = @chef.recipes.paginate(page: params[:page], per_page: 3)
  end
  
  private
    
    def chef_params
      params.require(:chef).permit(:chefname, :email, :password)
    end
    
    def set_chef
      @chef = Chef.find(params[:id])
    end
    
    def require_same_user
      if current_user != @chef
        flash[:danger] = "You can only edit your profile"
        redirect_to root_path
      end
    end
  
end
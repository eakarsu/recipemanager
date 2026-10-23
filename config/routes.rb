Rails.application.routes.draw do
  get '/api/health', to: 'health#show'
  root 'pages#home'
  
  get '/home', to: 'pages#home'
  

  resources :recipes do
    member do
      post 'like'
    end
  end
  
  resources :chefs, except: [:new, :destroy]
  get '/register', to: 'chefs#new'
  
  get '/login', to: 'logins#new'
  post '/login', to: 'logins#create'
  get '/logout', to: 'logins#destroy'
 
  resources :styles, only: [:new, :create, :show]
  resources :ingredients, only: [:new, :create, :show]
  
  
end

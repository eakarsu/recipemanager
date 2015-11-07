class Ingredient < ActiveRecord::Base
  validates :name, presence: true, length:{ minimum: 2, maximum: 25}
end
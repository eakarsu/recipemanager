require 'test_helper'

class ChefTest < ActiveSupport::TestCase
  
  def setup
    @chef = Chef.new(chefname: "john", 
            email: "john@example.com")

  end
  
  test "chef should be valid" do
    assert @chef.valid?
  end
  
  test "chef name should be present" do
    @chef.chefname = ""
    assert_not @chef.valid?
  end
  
  test "chewf name length should not be too long" do
    @chef.chefname = "a" * 41
    assert_not @chef.valid?
  end
  
  test "chef name length should not be too short" do
    @chef.chefname = "aa"
    assert_not @chef.valid?
  end  
  
  test "email should be present" do
    @chef.email = ""
    assert_not @chef.valid?
  end
  
  test "email length should be within bounds" do
    @chef.email = "a" * 101 + "@exampl.com"
    assert_not @chef.valid?
  end
  
  test "email address should be unique" do
    @dup_chef = @chef.dup
    @dup_chef.email = @chef.email.upcase
    @chef.save
    assert_not @dup_chef.valid?
  end
  test "email validation should accept valid addresses" do
    valid_addresses = %w[user@eee.com R_TO-DS@eee.hello.com user@example.com first.alst@saa.au]
    valid_addresses.each do |val|
      @chef.email = val
      assert @chef.valid?, '#{val.inspect} should be valid'
    end
    
  end
  
  test "email validation should reject valid addresses" do
    invalid_addresses = %w[user@eee R_TO-DS user@example. first.alst@saa+33.au]
    invalid_addresses.each do |val|
      @chef.email = val
      assert_not @chef.valid?, '#{val.inspect} should be invalid'
    end
  end
  
end

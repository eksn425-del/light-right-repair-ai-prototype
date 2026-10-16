obj_path = "E:/AI项目/light_equity_project/outputs/light_product_2026_06_02/recommended_conservative_model/candidate_01_modified_full_site.obj"
skp_path = "E:/AI项目/light_equity_project/outputs/light_product_2026_06_02/recommended_conservative_model/candidate_01_modified_full_site.skp"
log_path = "E:/AI项目/light_equity_project/outputs/light_product_2026_06_02/recommended_conservative_model/sketchup_obj_to_skp.log"

def write_log(path, message)
  File.open(path, "a:utf-8") { |file| file.puts("#{Time.now}: #{message}") }
end

UI.start_timer(1.0, false) do
  begin
    write_log(log_path, "Start import: #{obj_path}")
    model = Sketchup.active_model
    model.entities.clear!
    status = model.import(obj_path, false)
    unless status
      write_log(log_path, "OBJ import returned false")
      next
    end
    model.save(skp_path)
    write_log(log_path, "Saved SKP: #{skp_path}")
  rescue => error
    write_log(log_path, "FAILED #{error.class}: #{error.message}")
  ensure
    write_log(log_path, "Quit SketchUp")
    Sketchup.quit
  end
end
